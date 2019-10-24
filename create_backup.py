import argparse
import datetime
import logging
import os
import random
import smtplib
import string
import subprocess
from logging.handlers import RotatingFileHandler

import boto3

import config


def get_random_string(length=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


logger = logging.getLogger()
logger.setLevel(logging.INFO)

rotating_handler = RotatingFileHandler('logs.log', maxBytes=250 * 1000, backupCount=5)
logger.addHandler(rotating_handler)

per_backup_log_filename = '{}.log'.format(get_random_string(6))
per_backup_handler = logging.FileHandler(per_backup_log_filename)
logger.addHandler(per_backup_handler)

formatter = logging.Formatter('%(asctime)-18s %(levelname)-8s %(message)s', datefmt='%d.%m.%y %H:%M:%S')
rotating_handler.setFormatter(formatter)
per_backup_handler.setFormatter(formatter)

parser = argparse.ArgumentParser()
parser.add_argument('--config-path', type=str, help='Path to config.', required=True)
args = parser.parse_args()

config = config.get_config(args.config_path)


def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=config['S3_ACCESS_KEY_ID'],
        aws_secret_access_key=config['S3_SECRET_KEY'],
        endpoint_url=config['S3_ENDPOINT_URL'],
    )


def get_s3_path(filename):
    return '{}{}'.format(config['S3_PATH'], filename)


def push_to_s3(backup_save_path, filename):
    s3 = get_s3_client()
    s3.upload_file(backup_save_path, config['S3_BUCKET_NAME'], get_s3_path(filename))


def get_backup_archive_name():
    return '{}_{}.gz'.format(
        config['BACKUP_ARCHIVE_NAME_PREFIX'],
        datetime.datetime.now().strftime('%d-%m-%Y-_%H-%M-%S'),
    )


def get_backup_save_path(filename):
    return os.path.join(config['BACKUPS_DIR'], filename)


def get_file_size(backup_save_path):
    bytes = os.path.getsize(backup_save_path)
    mbs = round(bytes / 1024 / 1024, 3)
    return mbs


def get_backup_command(backup_save_path):
    command = 'pg_dump --no-password -h {} -p {} -U {} -d {} ' \
              '| gzip > {}'.format(
        config['PG_HOST'],
        config['PG_PORT'],
        config['PG_USER'],
        config['PG_DATABASE'],
        backup_save_path,
    )

    if config['DOCKER_MODE_ON']:
        command = 'docker exec -t {} '.format(config['DOCKER_CONTAINER_NAME']) + command

    return command


def send_report_to_email():
    with open(per_backup_log_filename, 'r') as f:
        message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(config['EMAIL_HOST_USER'],
                                                               config['EMAIL_SEND_TO'],
                                                               config['EMAIL_SUBJECT'],
                                                               f.read())

    server = smtplib.SMTP_SSL(config['EMAIL_HOST'], config['EMAIL_PORT'], timeout=10)
    try:
        server.ehlo(config['EMAIL_HOST_USER'])
        server.login(config['EMAIL_HOST_USER'], config['EMAIL_HOST_PASSWORD'])
        server.auth_plain()
        server.sendmail(config['EMAIL_HOST_USER'], config['EMAIL_SEND_TO'], message)
    finally:
        server.quit()


if __name__ == '__main__':
    backup_start_time = datetime.datetime.now()
    backup_archive_name = get_backup_archive_name()
    backup_save_path = get_backup_save_path(backup_archive_name)
    backup_command = get_backup_command(backup_save_path)

    logger.info('> > > Starting backup pipeline.')
    logger.info('Backup save path: {}'.format(backup_save_path))
    logger.info('Backup command: {}'.format(backup_command))

    try:
        ps = subprocess.Popen(backup_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ps.communicate(timeout=config['BACKUP_TIMEOUT'])[0]

        backup_created_time = datetime.datetime.now() - backup_start_time

        logger.info('Success backup created in {} secs ({} minutes). File size: {} mb.'.format(
            backup_created_time.seconds,
            round(backup_created_time.seconds / 60, 3),
            get_file_size(backup_save_path),
        ))
    except subprocess.TimeoutExpired:
        logger.error('Timeout (max {} secs) error.'.format(config['BACKUP_TIMEOUT']))

    if config['S3_ON']:
        try:
            s3_pushing_start_time = datetime.datetime.now()
            logger.info('Starting pushing to S3. Bucket: {}, s3 path: {}'.format(
                config['S3_BUCKET_NAME'],
                get_s3_path(backup_archive_name),
            ))

            push_to_s3(backup_save_path, backup_archive_name)

            s3_pushing_time = datetime.datetime.now() - s3_pushing_start_time
            logger.info('Success pushed to s3 in {} secs ({} minutes).'.format(
                s3_pushing_time.seconds,
                round(s3_pushing_time.seconds / 60, 3),
            ))
        except Exception as e:
            logger.exception("Failed pushing to s3:")

    logger.info('End backup pipeline.')

    if config['EMAIL_REPORT_ON']:
        logger.info('Sending backup report to {}.'.format(config['EMAIL_SEND_TO']))
        try:
            send_report_to_email()
            logger.info('Success sent backup report to {}.'.format(config['EMAIL_SEND_TO']))
        except Exception as e:
            logger.exception('Failed send report to email:')

    os.remove('./{}'.format(per_backup_log_filename))

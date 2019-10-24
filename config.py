import environ


def get_config(config_path):
    env = environ.Env()
    env.read_env(config_path)

    return {
        'BACKUPS_DIR': env('BACKUPS_DIR'),
        'BACKUP_TIMEOUT': int(env('BACKUP_TIMEOUT', default=3600)),
        'BACKUP_ARCHIVE_NAME_PREFIX': env('BACKUP_ARCHIVE_NAME_PREFIX', default='dump'),

        'PG_HOST': env('PG_HOST', default='localhost'),
        'PG_PORT': int(env('PG_PORT', default=5432)),
        'PG_USER': env('PG_USER'),
        'PG_DATABASE': env('PG_DATABASE'),

        'DOCKER_MODE_ON': env.bool('DOCKER_MODE_ON', default=False),
        'DOCKER_CONTAINER_NAME': env('DOCKER_CONTAINER_NAME', default=None),

        'S3_ON': env.bool('S3_ON', default=False),
        'S3_ACCESS_KEY_ID': env('S3_ACCESS_KEY_ID', default=None),
        'S3_SECRET_KEY': env('S3_SECRET_KEY', default=None),
        'S3_ENDPOINT_URL': env('S3_ENDPOINT_URL', default=None),
        'S3_BUCKET_NAME': env('S3_BUCKET_NAME', default=''),
        'S3_PATH': env('S3_PATH', default=''),

        'EMAIL_REPORT_ON': env.bool('EMAIL_REPORT_ON', default=False),
        'EMAIL_HOST': env('EMAIL_HOST'),
        'EMAIL_PORT': int(env('EMAIL_PORT', default=465)),
        'EMAIL_HOST_USER': env('EMAIL_HOST_USER'),
        'EMAIL_HOST_PASSWORD': env('EMAIL_HOST_PASSWORD'),
        'EMAIL_SEND_TO': env('EMAIL_SEND_TO'),
        'EMAIL_SUBJECT': env('EMAIL_SUBJECT'),
    }

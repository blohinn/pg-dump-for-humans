# pg_dump for humans

This tool is python wrapper on pg_dump with some usable features as:

- Docker support (backup from docker container with postgres);
- Pushing backups to S3-compatible storages support;
- Copy backups to another host with `scp` command support;
- Logging and email reporting;
- Flexible configuration with config files;

**Disclaimer**: this tool i created for personal purpose. Some features may not be designed as you need. Use at your own risk and always check the created backups (at least for the first time).

## Quick start

**Installing**: create virtual enviroment and install requirements from `requirements.txt`. Or simply install requirements for global python interpetator (python3.6 tested).

In the root of repository you can see `.config_example` config file. You can copy this config for each project. 

Configuration description:
```
# Common backup settings

# Backups will be created in this dir. Make sure the directory exist.
BACKUPS_DIR=/home/username/backups
BACKUP_TIMEOUT=3600 # seconds
# Archive will be named as <BACKUP_ARCHIVE_NAME_PREFIX>_%d-%m-%Y-_%H-%M-%S
BACKUP_ARCHIVE_NAME_PREFIX=dump

PG_HOST=localhost
PG_PORT=5432
PG_USER=username
PG_DATABASE=username

# Backup from docker container
DOCKER_MODE_ON=True
DOCKER_CONTAINER_NAME=e1871c7467a3

# S3 storage support
S3_ON=True
S3_ACCESS_KEY_ID=7LOL44XC5O32A23
S3_SECRET_KEY=Lz7DnFEN5FvaoLOLTbHY0yzU5cb2SsB9hrzbMUuL
S3_ENDPOINT_URL=https://s3.us-west-1.wasabisys.com
S3_BUCKET_NAME=backups
S3_PATH=backups/

# Email report
EMAIL_REPORT_ON=True
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_HOST_USER=smtpemail@smtpemail.ru
EMAIL_HOST_PASSWORD=ps2fv1dlf3
EMAIL_SEND_TO=admin@yandex.ru
EMAIL_SUBJECT=Backup report for my database

# SCP support
SCP_ON=False
SCP_REMOTE_HOST=222.132.45.12
SCP_REMOTE_PORT=22
SCP_REMOTE_USER=username
# Backups will be copy to this dir. Make sure the directory exist.
SCP_REMOTE_DIR=/home/username/backups
```

You can easily turn on / turn off featues by set `FEATURE_ON` options.

Now you can run scrpit manualy, check the `logs.log` and backup validity:

```
python3 create_backup.py --config-path .config_example.
```

Unzip `<dump_name>.gz` file and check backup, for example with nano. Trying to restore backup on test database. Check logs.

Now you can add backup command to `crontab`:

```
0 0 * * * cd /home/blohin/pg-dump-for-humans/ && python3 create_backup.py --config-path .project_midnight
```

This command create backus every midnight. 
**Be sure that backup command executed from backup-tool dir and requirements installed.**

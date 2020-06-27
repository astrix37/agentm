import os

DEBUG=True
DOWNLOAD_BUCKET = 'smitty-mods'
BACKUP_BUCKET = 'betagamebackups'
BUCKET_PREFIX = 'mine'
MODS_FOLDER = 'plugins'


def get_environment_variable(var):
    return os.environ.get(var)
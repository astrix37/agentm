from .base import *
import os

def get_environment_variable(var):
    return os.environ.get(var)

TAR_FOLDER = "/tmp/{}"
TAR_TEMPLATE = 'minecraft-{}--.tar.gz'

SERVER = "https://www.cjgamer.com/{}"

API_METHODS = ['POST']
MINECRAFT_SERVER_LOCATION = get_environment_variable('MINECRAFT_SERVER_LOCATION')
DEBUG=False
MODS_FOLDER = get_environment_variable('MODS_FOLDER')

SUPERVISOR_JOB_NAME = 'minecraftserver'
SUPERVISOR_SERVER_URL = 'unix:///tmp/supervisor-mine.sock'

VALID_COMMANDS = ['op', 'deop', 'say', 'kill', 'tp', 'gamemode', 'time', 'difficulty', 'seed']

LOGGING_CONFIG = {
   'version': 1,
    'formatters': {
            'default': {
            'format': '%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s',
        }
    },

    'handlers': {
        'general': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/apps/agentm-general.log',
            'formatter': 'default'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
    },

    'root': {
        'level': 'INFO',
        'handlers': ['general', 'console']
    }
}


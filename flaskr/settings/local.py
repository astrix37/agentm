from .base import *

API_METHODS = ['GET', 'POST']
MINECRAFT_SERVER_LOCATION = "F:\Dev\minecraft_servers\server1"

TAR_FOLDER = "F:/Dev/agentm/{}"

SERVER = "http://localhost:8000/{}"

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
            'default': {
            'format': '%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s',
        }
    },

    'handlers': {
        'general': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'F:\\Dev\\agentm\\logs\\general.log',
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
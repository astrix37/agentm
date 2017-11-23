from base import *
import os

def get_environment_variable(var):
    return os.environ.get('MINECRAFT_SERVER_LOCATION')


API_METHODS = ['POST']
MINECRAFT_SERVER_LOCATION = get_environment_variable('MINECRAFT_SERVER_LOCATION')
DEBUG=False

SUPERVISOR_JOB_NAME = 'minecraftserver'
SUPERVISOR_SERVER_URL = 'unix:///tmp/supervisor-mine.sock'

VALID_COMMANDS = ['op', 'deop', 'say', 'kill', 'tp', 'gamemode', 'time', 'difficulty', 'seed']
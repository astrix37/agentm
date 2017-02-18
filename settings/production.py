from base import *
import os

def get_environment_variable(var):
    pass

API_METHODS = ['POST']
MINECRAFT_SERVER_LOCATION = "/apps/mine/server189"
DEBUG=False

SUPERVISOR_JOB_NAME = 'minecraftserver'
SUPERVISOR_SERVER_URL = 'unix:///tmp/supervisor-mine.sock'

VALID_COMMANDS = ['op', 'deop', 'say', 'kill', 'tp', 'gamemode', 'time']
import os
import logging

from logging.config import dictConfig
from flask import Flask, render_template, url_for, jsonify, request
from flask_cors import CORS, cross_origin


def configure_application(root):

    app = Flask(
        root
    )
    app.config.from_object("settings.local" if 'FLASK_SETTINGS_FILE' not in os.environ else os.environ['FLASK_SETTINGS_FILE'])
    CORS(app)
    dictConfig(app.config['LOGGING_CONFIG'])  
    return app
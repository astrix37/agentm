import os
from logging.config import dictConfig
from flask import Flask
from flask_cors import CORS

def create_app(root):
    app = Flask(__name__)
    app.config.from_object("flaskr.settings.local" if 'FLASK_SETTINGS_FILE' not in os.environ else os.environ['FLASK_SETTINGS_FILE'])
    CORS(app)
    dictConfig(app.config['LOGGING_CONFIG'])

    # Blue Prints
    with app.app_context():
        from . import server
        app.register_blueprint(server.bp)

    return app

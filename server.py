import json
import os, sys
import requests
import logging

from logging import FileHandler 
from flask import Flask, render_template, url_for, jsonify, request
from flask_cors import CORS, cross_origin
from libs.minecraft_server import MinecraftServer
from libs.decoraters import protect_view

#rom supervisor.supervisorctl import *
#rom supervisor.options import ClientOptions

logging.basicConfig(format='%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def configure_application():
    app = Flask(__name__)
    app.config.from_object("settings.local" if 'FLASK_SETTINGS_FILE' not in os.environ else os.environ['FLASK_SETTINGS_FILE'])
    CORS(app)

    return app

app = configure_application()
server_details = MinecraftServer()
methods = app.config['API_METHODS']

@app.route('/')
def home():
    var = {}
    return render_template("index.html", title="Oh, hello", **var)

@app.route('/ops/', methods=methods)
@protect_view
def ops():
    return jsonify(server_details.get_ops()), 200


@app.route('/banned/', methods=methods)
@protect_view
def banned():
    return jsonify(server_details.get_banned_players()), 200


@app.route('/properties/', methods=methods)
@protect_view
def properties():
    return jsonify(server_details.get_properties()), 200


@app.route('/forge-log/', methods=methods)
@protect_view
def forge_log():
    return jsonify(server_details.get_latest_forge_log()), 200


@app.route('/general-log/', methods=methods)
@protect_view
def general_log():
    return jsonify(server_details.get_latest_log()), 200


@app.route('/blueprints/', methods=methods)
@protect_view
def blueprints():
    return jsonify(server_details.get_blueprints()), 200


@app.route('/core-blueprints/', methods=methods)
@protect_view
def core_blueprints():
    return jsonify(server_details.get_core_blueprints()), 200


@app.route('/forge-mods/', methods=methods)
@protect_view
def mods():
    return jsonify(server_details.get_mods()), 200


@app.route('/install-mod/', methods=methods)
@protect_view
def install():
    file = request.form['mod']
    mod_folder = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "mods")
    file_path = os.path.join(mod_folder, file)

    logger.info("A request has come in to install {}".format(file))

    try:
        if os.path.exists(file_path):
            logger.info("A file by this name already exists. No action taken.")
            return jsonify({"status": "file_already_exists"}), 409
        else:
            logger.info("Now downloading {}...".format(file))
            target = '{}/mods/{}'.format(app.config['DOWNLOAD_LOCATION'], file)
            logger.info("Target is {}".format(target))
            response = requests.get(target, verify=False, timeout=5)

            with open(file_path, 'wb') as handle:
                handle.write(response.content)

            logger.info("Successfully installed")
            return jsonify({"status": "file_installed"}), 200
    except Exception as ex:
        logger.info("An error has occured during installation: {}".format(ex))
        return jsonify({"status": "an_error_as_occured"}), 500
        

@app.route('/remove-mod/', methods=methods)
@protect_view
def remove():
    file = request.form['mod']
    mod_folder = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "mods")
    file_path = os.path.join(mod_folder, file)

    logger.info("A request has come in to remove {}".format(file))

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("This mod did exist. It has now been removed")
            return jsonify({"status": "file_removed"}), 200

        logger.info("This mod does not exist. No action taken")
        return jsonify({"status": "file_not_present"}), 404
    except Exception as ex:

        logger.info("An error has occured during removal: {}".format(ex))
        return jsonify({"status": "an_error_has_occured"}), 500


@app.route('/command/', methods=methods)
@protect_view
def command():
    logger.info("A command has come in")
    try:
        command_string = request.form['command']
        command = command_string.split(' ')

        if not command[0] in app.config['VALID_COMMANDS']:
            return jsonify({"status": "failure", "command": "Command denied"}), 403
            
        if command[0] == "op" and command_string != "op astrix37":
            return jsonify({"status": "failure", "command": "Command denied for user"}), 403

        options = ClientOptions()
        options.realize([], doc=__doc__)
        options.serverurl = app.config['SUPERVISOR_SERVER_URL']

        c = Controller(options)      
        supervisor = c.get_supervisor()
        info = supervisor.getProcessInfo(app.config['SUPERVISOR_JOB_NAME'])

        sys.stdout = open('/proc/{}/fd/0'.format(info['pid']), 'w')
        print command_string
        sys.stdout = sys.__stdout__
        logger.info("Command successfully executed")
        return jsonify({"status": "success", "command": command_string}), 200
    except Exception as ex:
        logger.info("Command failed: {}".format(ex))
        return jsonify({"status": "failure", "command": str(ex)}), 500


if __name__ == '__main__':
    app.run(threaded=True)
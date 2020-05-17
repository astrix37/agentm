from libs.configure import configure_application
app = configure_application(__name__)

import boto3
import json
import logging
import os
import requests
import sys
import traceback

from datetime import datetime
from flask import Flask, render_template, url_for, jsonify, request
from logging import FileHandler 
from libs.minecraft_server import MinecraftServer
from libs.decoraters import protect_view
from libs.backup import BackupMineCraft

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

server_details = MinecraftServer()
methods = app.config['API_METHODS']

@app.route('/')
def home():
    var = {}
    return render_template("index.html", title="Oh, hello", **var)


#Standard View 1
@app.route('/install-mod/', methods=methods)
@protect_view
def install():
    file = request.form['mod']
    mod_folder = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], app.config['MODS_FOLDER'])
    file_name = file[file.rfind('/') + 1:]
    file_path = os.path.join(mod_folder, file_name)

    logger.info("A request has come in to install {}".format(file_name))

    try:
        if os.path.exists(file_path):
            logger.info("A file by this name already exists. No action taken.")
            return jsonify({"result": "file_already_exists"}), 409
        else:
            logger.info("Now downloading {} from s3...".format(file))
            
            s3 = boto3.client('s3', region_name='ap-southeast-2')
            s3.download_file(
                Bucket=app.config['DOWNLOAD_BUCKET'],
                Key=file,
                Filename=file_path
            )

            logger.info("Successfully installed {} to {}".format(file, file_path))
            return jsonify({"result": "{} has successfully been installed".format(file)}), 200
    except Exception as ex:
        logger.error(traceback.format_exc())
        return jsonify({"result": str(ex)}), 500
        

#Standard View 2
@app.route('/remove-mod/', methods=methods)
@protect_view
def remove():
    file = request.form['mod']
    mod_folder = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], app.config['MODS_FOLDER'])
    file_name = file[file.rfind('/') + 1:]
    file_path = os.path.join(mod_folder, file_name)

    logger.info("A request has come in to remove {}".format(file))
    logger.info("Now searching for {}".format(file_name))

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("This mod did exist. It has now been removed")
            return jsonify({"result": "{} has been removed".format(file)}), 200

        logger.info("This mod does not exist. No action taken")
        return jsonify({"result": "Cannot remove {}. File not found".format(file)}), 404
    except Exception as ex:
        logger.error(traceback.format_exc())
        return jsonify({"result": str(ex)}), 500


#Standard View 3
@app.route('/list-mods/', methods=methods)
@protect_view
def mods():
    try:
        return jsonify({'result': server_details.get_mods()}), 200
    except Exception as ex:
        logger.error(traceback.format_exc())
        return jsonify({'result': str(ex)}), 500


#Standard View 4
@app.route('/list-logs/', methods=methods)
@protect_view
def list_logs():
    try:
        return jsonify({'result': server_details.list_logs()}), 200
    except Exception as ex:
        logger.error(traceback.format_exc())
        return jsonify({'result': str(ex)}), 500


#Standard View 5
@app.route('/get-log/', methods=methods)
@protect_view
def get_log():

    try:
        logs = server_details.list_logs()
        log_file = request.form['log_file']
   
        if log_file in logs:
            return jsonify({'result': server_details.get_log(log_file)}), 200
        else:
            return jsonify({"result": "log_file_not_found"}), 404
        
    except Exception as ex:
        return jsonify({'result': str(ex)}), 500


#Standard View 6
@app.route('/create-backup/', methods=methods)
@protect_view
def create_backup():

    try:
        #Naming Vars
        server_name = request.form['server_name']
        user_name = request.form['user_name']
        salt = request.form['salt']

        #Helper Vars
        template = '{}-{}-{}-{}.tar.gz'
        timestamp = "{}-{}-{}".format(datetime.now().year, datetime.now().month, datetime.now().day)
        folder = app.config['TAR_FOLDER']

        #Key Vars
        source_dir = app.config['MINECRAFT_SERVER_LOCATION']
        target_file = template.format(server_name, timestamp, user_name, salt)
        target_file_abs = folder.format(target_file)

        BackupMineCraft(
            source_dir,
            target_file,
            target_file_abs,
            app.config['BACKUP_BUCKET'],
            "{}/{}".format(app.config['BUCKET_PREFIX'], target_file),
            salt,
            app.config['SERVER']
        )

        return jsonify({'result': 'Backup initiated. Please check back in a few minutes'}), 200

    except Exception as ex:
        logger.error(traceback.format_exc())
        return jsonify({'result': 'Unable to process backup'}), 500

    


##Additional Views Specific to Minecraft
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
        sys.stdout = sys.__stdout__
        logger.info("Command successfully executed")
        return jsonify({"status": "success", "command": command_string}), 200
    except Exception as ex:
        logger.info("Command failed: {}".format(ex))
        return jsonify({"status": "failure", "command": str(ex)}), 500


if __name__ == '__main__':
    app.run(threaded=True)
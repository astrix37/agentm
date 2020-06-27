import logging
import os
import json
from flask import Blueprint
from flask import render_template, request, current_app as app
from flaskr.libs.decoraters import protect_view
from flaskr.libs.exceptions import InsufficientDataException, NotFoundException, BadDataException
from flaskr.libs.minecraft_server import MinecraftCore

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
methods = app.config['API_METHODS']
bp = Blueprint('server', __name__, url_prefix='/')


@bp.route('/')
def home():
    var = {}
    return render_template("index.html", title="Oh, hello", **var)


@bp.route('/create_backup/', methods=methods)
@protect_view(error_response="Error - There was an issue when trying to create a backup")
def create_backup():
    result = MinecraftCore.create_backup(request)
    return result


@bp.route('/get_admins/', methods=methods)
@protect_view(error_response="Error - Unable to get the admin file")
def get_admins():
    admin_file_location = "ops.json"
    file = MinecraftCore.get_file(admin_file_location)
    return json.loads(file)


@bp.route('/get_file/', methods=methods)
@protect_view(error_response="An error occured while trying to read this file")
def get_file():
    if 'target_file' not in request.form:
        raise InsufficientDataException("Missing form data 'log_file'")

    requested_file = request.form['target_file']
    file = MinecraftCore.get_file(requested_file)
    return file


@bp.route('/save_file/', methods=methods)
@protect_view(error_response="An error occured while trying to save this file")
def save_file():
    if 'input' not in request.files:
        raise InsufficientDataException("Missing form file 'input'")

    file_name = request.form['file_name']
    file_obj = request.files['input']
    logger.info(file_name)
    MinecraftCore.save_file(file_name, file_obj)
    return "File has been save successfully"


@bp.route('/get_log/', methods=methods)
@protect_view(error_response="Unable to get log")
def get_log():  #TODO: Sanitize data to logs folder
    if 'log_file' not in request.form:
        raise InsufficientDataException("Missing form data 'log_file'")

    logs_folder = "logs"
    log_file = request.form['log_file']
    listing = MinecraftCore.list_files(logs_folder)
    if log_file in listing[2]:
        path = os.path.join(logs_folder, log_file)
        return MinecraftCore.get_file(path)
    raise NotFoundException("{} does not exist or could not be found".format(log_file))


@bp.route('/get_properties/', methods=methods)
@protect_view(error_response="Error - Unable to get the properties file")
def get_properties():
    file_location = "server.properties"
    file = MinecraftCore.get_file(file_location)
    compiled = []
    for line in file.split('\n'):
        lines = line.split('=')
        if len(lines) == 1:
            compiled.append({"key": lines[0], "value": ''})
        else:
            compiled.append({"key": lines[0], "value": lines[1]})
    return compiled


@bp.route('/list_files/', methods=methods)
@protect_view(error_response="Unhandled error - Files could not be listed for the path specified")
def list_files():
    if 'path' not in request.form:
        raise InsufficientDataException("Missing form data 'path'")

    path = request.form['path']
    listing = MinecraftCore.list_files(path)
    folders = listing[1]
    files = listing[2]
    return {"folders": folders, "files": files}


@bp.route('/install_mod/', methods=methods)  # Modify Mod
@protect_view(error_response="Unhandled error - This file could not be installed")
def install_mod():  #TODO: Sanitize data
    if 's3_mod' not in request.form:
        raise InsufficientDataException("Missing form data 's3_mod'")

    s3_file = request.form['s3_mod']
    install_folder = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], app.config['MODS_FOLDER'])
    result = MinecraftCore.install(install_folder, s3_file)
    return result


@bp.route('/delete_file/', methods=methods)  # Modify Mod
@protect_view(error_response="Unable to remove file")
def delete_file():
    if 'file' not in request.form:
        raise InsufficientDataException("Missing form data 'file'")
    if 'plugin' in request.form and 'path' in request.form:
        raise BadDataException("You can provide 'plugin' or 'path' but not both")
    if 'plugin' not in request.form and 'path' not in request.form:
        raise InsufficientDataException("Please specify 'plugin' if this is a plugin, or 'path' to specify delete path")

    if 'plugin' in request.form:
        s3_file = request.form['file']
        target_file = s3_file[s3_file.rfind('/') + 1:]
        install_folder = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], app.config['MODS_FOLDER'])
    else:
        path = request.form['path']
        target_file = request.form['file']
        install_folder = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], path)

    result = MinecraftCore.delete_file(install_folder, target_file)
    return result


@bp.route('/list_mods/', methods=methods)
@protect_view(error_response="Unable to list available mods")
def mods():
    path = app.config['MODS_FOLDER']
    listing = MinecraftCore.list_files(path)
    return listing[2]


@bp.route('/list_logs/', methods=methods)
@protect_view(error_response="Unable to list available logs")
def list_logs():
    logs_folder = "logs"
    listing = MinecraftCore.list_files(logs_folder)
    return listing[2]


@bp.route('/command/', methods=methods)
@protect_view(error_response="Unable to execute command")
def command():
    if 'command' not in request.form:
        raise InsufficientDataException("Missing form data 'command'")

    command_string = request.form['command']
    result = MinecraftCore.command(request, command)
    return result

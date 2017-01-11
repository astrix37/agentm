import json
import os
import requests
from flask import Flask, render_template, url_for, jsonify
from flask_cors import CORS, cross_origin
from libs.minecraft_server import MinecraftServer
from libs.decoraters import protect_view


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


if __name__ == '__main__':
    app.run(threaded=True)
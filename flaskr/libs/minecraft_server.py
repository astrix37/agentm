import json
import os
from flask import current_app as app

class MinecraftServer:

	def get_ops(self):
		ops = json.loads(open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "ops.json")).read())
		for op in ops:
			del op['uuid']
		return ops

	def get_banned_players(self):
		data = open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "banned-players.json")).read()
		data = json.loads(data)
		return data

	def get_properties(self):
		return open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "server.properties")).readlines()
				
	def get_latest_forge_log(self):
		fml_activity = open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "logs", "fml-server-latest.log")).readlines()
		if len(fml_activity) > 200:
			fml_activity = fml_activity[-200:]
		return fml_activity

	def get_latest_log(self):
		return open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "logs", "latest.log")).readlines()

	def get_blueprints(self):
		return next(os.walk(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "config", "bp")))[2]

	def get_core_blueprints(self):
		return json.loads(open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "config", "bp", "blueprint.json")).read())

	def get_mods(self):
		path = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], app.config['MODS_FOLDER'])
if not os.path.exists(path):
	os.mkdir(path)
		return next(os.walk(path))[2]

	def list_logs(self):
		return next(os.walk(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "logs")))[2]

	def get_log(self, logfile):
		return open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "logs", logfile)).readlines()
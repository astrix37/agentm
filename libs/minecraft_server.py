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
		properties = []
		raw = open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "server.properties")).readlines()
		for prop in raw:
			properties.append(prop.replace("\n", ""))
		return properties
		

	def get_latest_forge_log(self):
		fml_activity = open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "logs", "fml-server-latest.log")).readlines()
		if len(fml_activity) > 50:
			fml_activity = fml_activity[-50:]
		return fml_activity

	def get_latest_log(self):
		return open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "logs", "latest.log")).readlines()

	def get_blueprints(self):
		return next(os.walk(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "config", "bp")))[2]

	def get_core_blueprints(self):
		return json.loads(open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "config", "bp", "blueprint.json")).read())

	def get_mods(self):
		return next(os.walk(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], "mods")))[2]
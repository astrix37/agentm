import boto3
import logging
import os
import sys
import traceback
from datetime import datetime
from flask import current_app as app
from flaskr.libs.backup import BackupMineCraft
from flaskr.libs.exceptions import NotFoundException
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MinecraftCore:
	"""
		Minecraft core does all the heavy lifting for Agent M, and is where any data sanitization should happen
	"""
	@staticmethod
	def get_file(file_path):
		base_path = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'])
		target_path = os.path.abspath(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], file_path))
		if target_path.startswith(base_path):
			return open(target_path).read()
		raise NotFoundException("The file you have requested does not exist")

	@staticmethod
	def get_text_file(file_path):
		base_path = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'])
		target_path = os.path.abspath(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], file_path))
		if target_path.startswith(base_path):
			return open(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], file_path))
		raise NotFoundException("The file you have requested does not exist")

	@staticmethod
	def list_files(folder_path):
		base_path = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'])
		target_path = os.path.abspath(os.path.join(base_path, folder_path))
		try:
			if target_path.startswith(base_path):
				return next(os.walk(os.path.join(app.config['MINECRAFT_SERVER_LOCATION'], target_path)))
		except Exception:
			raise NotFoundException("The folder you have requested does not exist.")
		raise NotFoundException("The folder you have requested does not exist.")

	@staticmethod
	def save_file(file_name, file_obj):
		base_path = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'])
		target_path = os.path.abspath(os.path.join(base_path, file_name))
		if target_path.startswith(base_path):
			file_obj.save(target_path)
			return "File has been saved", 200

		raise NotFoundException("Agent cannot save {}. Invalid location".format(file_name))

	@staticmethod
	def delete_file(folder_path, file_name):
		base_path = os.path.join(app.config['MINECRAFT_SERVER_LOCATION'])
		target_path = os.path.abspath(os.path.join(folder_path, file_name))
		if target_path.startswith(base_path):
			logger.info("A request has come in to remove {}".format(file_name))
			logger.info("Now searching for {}".format(target_path))

			if os.path.exists(target_path):
				os.remove(target_path)
				logger.info("This file did exist. It has now been removed")
				return "{} has been removed".format(file_name)
			logger.info("File '{}' does not exist. No action taken".format(target_path))
		raise NotFoundException("Agent cannot remove {}. File not found".format(file_name))

	@staticmethod
	def install(install_folder, s3_file):
		file_name = s3_file[s3_file.rfind('/') + 1:]
		file_path = os.path.join(install_folder, file_name)

		logger.info("A request has come in to install {}".format(file_name))

		if os.path.exists(file_path):
			logger.info("A file by this name already exists. No action taken.")
			return "file_already_exists"
		else:
			logger.info("Now downloading {} from s3...".format(s3_file))

			s3 = boto3.client('s3', region_name='ap-southeast-2')
			s3.download_file(
				Bucket=app.config['DOWNLOAD_BUCKET'],
				Key=s3_file,
				Filename=file_path
			)

			logger.info("Successfully installed {} to {}".format(s3_file, file_path))
			return "{} has successfully been installed".format(s3_file)

	@staticmethod
	def create_backup(request):
		"""
			Gathers several vars from request data: server_name, user_name, salt
			Uses details to construct a file name, and sends a file of that name to S3 bucket
		"""
		# Naming Vars
		server_name = request.form['server_name']
		user_name = request.form['user_name']
		salt = request.form['salt']

		# Helper Vars
		template = '{}-{}-{}-{}.tar.gz'
		timestamp = "{}-{}-{}".format(datetime.now().year, datetime.now().month, datetime.now().day)
		folder = app.config['TAR_FOLDER']

		# Key Vars
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
		return 'Backup initiated. Please check back in a few minutes'


	@staticmethod
	def command(request, command):
		logger.info("A command has come in")

		command_parts = command.split(' ')

		if not command_parts[0] in app.config['VALID_COMMANDS']:
			return jsonify({"status": "failure", "command": "Command denied"}), 403

		if command_parts[0] == "op" and command != "op astrix37":
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
		return {"status": "success", "command": command}

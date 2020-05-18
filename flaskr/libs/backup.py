import boto3
import logging
import os
import requests
import tarfile
import threading
import traceback
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BackupMineCraft(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, source_dir, target_file, target_file_abs, bucket, key, salt, server):

        self.source_dir = source_dir
        self.target_file = target_file
        self.target_file_abs = target_file_abs
        self.key = key
        self.bucket = bucket
        self.salt = salt
        self.server = server
        self.size = 0

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        created = False
        size = "ERROR"

        try:
            logger.info("Creating backup")
            with tarfile.open(self.target_file_abs, "w:gz") as tar:
                tar.add(self.source_dir, arcname=os.path.basename(self.source_dir))
            created = True

            logger.info("Sending to S3")
            with open(self.target_file_abs, 'rb') as data:
                s3 = boto3.resource('s3', region_name='ap-southeast-2')
                bucket = s3.Bucket(self.bucket)
                cfg = boto3.s3.transfer.TransferConfig(use_threads=False)
                bucket.upload_fileobj(data, self.key, Config=cfg)

            self.size = self.file_size()

            logger.info("Removing file")
            os.remove(self.target_file_abs)
            created = False

            logger.info("Success")
            self.respond(True)

        except Exception as ex:
            logger.info("An error has occured")
            logger.info(traceback.format_exc())
            if created:
                os.remove(self.target_file_abs)

            self.respond(False)

    def respond(self, success):
        result = requests.post(
            self.server.format("console/api/create_backup_callback/"), 
            verify=False, 
            timeout=10,
            data={
                'auth_key': os.environ['KEY'],
                'size': self.size,
                'file': self.key,
                'salt': self.salt,
                'success': success
            }
        )
        logger.info("Callback result: {}".format(result))

    def file_size(self):

        if os.path.isfile(self.target_file_abs):
            file_name = self.target_file_abs
            file_info = os.stat(file_name)

            file_bytes = file_info.st_size

            for x in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
                if file_bytes < 1024.0:
                    return "%3.1f %s" % (file_bytes, x)
                file_bytes /= 1024.0

        return "ERR"
import boto3
import logging
import os
import requests
import tarfile
import threading
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

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        created = False

        try:
            logger.info("Creating backup")
            with tarfile.open(self.target_file_abs, "w:gz") as tar:
                tar.add(self.source_dir, arcname=os.path.basename(self.source_dir))
            created = True

            logger.info("Sending to S3")
            s3 = boto3.client('s3', region_name='ap-southeast-2')  
            s3.put_object(
                Bucket=self.bucket, 
                Key=self.key, 
                Body=open(self.target_file_abs, 'rb').read()
            )

            os.remove(self.target_file_abs)
            created = False

            logger.info("Done")
            self.respond(True)

        except Exception as ex:
            if created:
                os.remove(self.target_file_abs)

            self.respond(False)

    def respond(self, success):
        requests.post(
            self.server.format("console/api/create_backup_callback/"), 
            verify=False, 
            timeout=10,
            data={
                'auth_key': os.environ['KEY'],
                'file': self.key,
                'salt': self.salt,
                'success': success
            }
        )
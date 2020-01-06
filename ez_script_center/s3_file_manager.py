"""
Module containing a class for handling s3 file uploading and downloading
"""
import os
from itertools import zip_longest
from datetime import datetime as dt
from uuid import uuid4
from io import StringIO, BytesIO

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

from flask import current_app


class S3Manager:
    """
    Class for managing s3 file uploading and downloading.
    Instantiate object with connection info
    """
    def __init__(
        self,
        bucket_name,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        file_input_path="input_data/",
        file_result_path="result_data/"
    ):
        self._bucket_name = bucket_name
        self._input_path = file_input_path
        self._result_path = file_result_path

        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=Config(signature_version='s3v4', region_name='eu-central-1')
        )
        self.s3_bucket = self.s3_resource.Bucket(name=bucket_name)
        self.s3_client = self.s3_resource.meta.client

    # is it a result path or input path?
    def upload_fileobj(self, file_obj, file_name=None, is_result=False):
        """
        Automatically upload a given file like obj and return the
        location key.

        Args:
            file_obj (file like object): The object to be uploaded.
            file_name ('str', optional): The filename to used instead
                of the original one. If None, it will use the file's
                filename.
                Defaults to None.
            is_result (bool, optional): Should it upload to the result
                pathway specified on installation? By default it's False
                and uploads to the input path.
                Defaults to False.

        Returns:
            str: The key of the uploaded file.
        """
        if file_name is None:
            file_name = file_obj.filename

        path = self._input_path if not is_result else self._result_path

        # Adding a unique prefix, so it distributes better
        # kind of an overkill for now, but it won't hurt.
        # https://aws.amazon.com/blogs/aws/amazon-s3-performance-tips-tricks-seattle-hiring-event/
        timestamp = str(dt.now().isoformat())
        salt = uuid4().hex[:6]
        file_name = f"{salt}.{timestamp}.{file_name}"

        key = f"{path}{file_name}"
        self.s3_bucket.upload_fileobj(file_obj, key)

        return key

    def upload_files(self, files, is_result=False):
        """
        Wrapper around upload_fileobj method.

        Returns a dict with a key-value pairing of the form's name and
        the uploaded file's object.

        Args:
            files (dict of file like objects): A dictionary containing
                the file name and a file like object to be uploaded.
            is_result (bool, optional): Should it upload to the result
                pathway specified on installation? By default it's False
                and uploads to the input path.
                Defaults to False.

        Returns:
            dict of str: A dict containing a key which is the key of the
                passed dict and a corresponding string key for the S3
                file location of the uploaded file like object.

                See Notes for possible issues if passing a
                https://werkzeug.palletsprojects.com/en/0.16.x/datastructures/#werkzeug.datastructures.MultiDict

        Notes:
            If you pass request.files here as files it will work. But
            be aware that if multiple form fields have the same name,
            only the first pair will be saved here.
            Make sure to create unique names for form fields!
        """
        # Fix the naming if passing from none

        keys = {
            name: self.upload_fileobj(file_obj, file_name=name, is_result=is_result)
            for name, file_obj in files.items()
        }

        return keys

    def generate_presigned_links(self, files, expiration=3600):
        try:
            presigned_links = {}

            for name, key in files.items():
                presigned_links[name] = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self._bucket_name,
                        'Key': key,
                        'ResponseContentDisposition': f"attachment; filename = {name}"
                    },
                    ExpiresIn=expiration
                )
        except ClientError as e:
            current_app.logging.error(e)
            return None

        return presigned_links

    def download_fileobj(self, key):
        """
        Return a tuple with cleaned name and a BytesIO file like object
        of the requested object.
        """
        filename = key.split(".", 3)[-1]

        file_obj = BytesIO()
        self.s3_bucket.download_fileobj(key, file_obj)

        return (filename, file_obj)

    # def download_files(self, keys, file_obj):
    #     """
    #     This is a wrapper of download_fileobj method.

    #     Download multiple filelike_objects by their keys and return
    #     them in a dict.

    #     The passed keys, are the keys in the dict, while the value is a
    #     (cleaned filename, filelike obj) tuple.
    #     """
    #     files = {}

    #     for key in keys:
    #         files[key] = self.download_fileobj(key, file_obj=)

    #     return files

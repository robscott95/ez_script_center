"""
Module containing a class for handling s3 file uploading and downloading
"""
import os
from itertools import zip_longest
from datetime import datetime as dt
from uuid import uuid4

import boto3


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
            aws_secret_access_key=aws_secret_access_key
        )
        self.s3_bucket = self.s3_resource.Bucket(name=bucket_name)

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

    def upload_files(self, file_objs, file_names=None, is_result=False):
        """
        Wrapper around upload_fileobj method.

        Returns a set of keys of the newly created objects in S3.

        If file_names is passed it must be a list of str that is the
        same length as the file_objs sequence.
        Raises ValueError otherwise.

        Args:
            file_objs (list of file_objs): A list of file_objs.
            file_names (list of str, optional): A list of file_names.
                Has to contain only strings.
                Defaults to False.
            is_result (bool, optional): Should it upload to the result
                pathway specified on installation? By default it's False
                and uploads to the input path.
                Defaults to False.

        Returns:
            set of str: A set of keys for all the uploaded elements.

        Raises:
            ValueError: When not all elements in file_names are string.
        """

        if file_names is not None:
            if all(isinstance(ele, str) for ele in file_names):
                raise ValueError("The passed file_names contains a non-string element.")
        else:
            # Just to easily support zip_longest
            file_names = []

        keys = set(
            self.upload_fileobj(file_obj, file_name, is_result)
            for file_obj, file_name in zip_longest(file_objs, file_names)
        )

        return keys

    def download_fileobj(self, key):
        """
        Return a tuple with cleaned name and a file like object.
        """
        filename = key.split(".", 2)[-1]

        return (filename, self.s3_bucket.download_fileobj(key))

    def download_files(self, keys):
        """
        This is a wrapper of download_fileobj method.

        Download multiple filelike_objects by their keys and return
        them in a dict.

        The passed keys, are the keys in the dict, while the value is a
        (cleaned filename, filelike obj) tuple.
        """
        files = {}

        for key in keys:
            files[key] = self.download_fileobj(key)

        return files

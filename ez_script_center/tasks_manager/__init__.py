"""
Module for handling user defined tasks and it's respective forms.

In __init__ of your app please import and initialize the
TaskManager object.
"""
import inspect
from abc import ABC
from os.path import dirname, basename, join
from glob import glob

import celery

from ez_script_center import s3
from ez_script_center.database_manager import update_task_history_with_results

pwd = dirname(__file__)


class TasksManager:
    available_tasks = {}
    available_forms = {}

    def __init__(self):
        for x in glob(join(pwd, "*.py")):
            if not basename(x).startswith("__") and basename(x) != "scripts":
                __import__(
                    f"ez_script_center.tasks_manager.{basename(x)[:-3]}",
                    globals(),
                    locals(),
                )

    @staticmethod
    def _url_creator(url):
        """Make so that if URL is None, it makes the filename the url.
        """
        if url is None:
            frame = inspect.stack()[2]
            module = inspect.getmodule(frame[0])
            filename = module.__file__[:-3]
            # snake_case won't look good. More compliant url.
            filename = filename.replace("_", "-")
            url = basename(filename)

        return url

    @staticmethod
    def register_task(url=None):
        url = TasksManager._url_creator(url)

        def inner_func(task):
            TasksManager.__dict__["available_tasks"][url] = task
            return task

        return inner_func

    @staticmethod
    def register_form(url=None):
        url = TasksManager._url_creator(url)

        def inner_func(form):
            TasksManager.__dict__["available_forms"][url] = form
            return form

        return inner_func


class TaskBase(celery.Task):

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        try:
            result = retval["result"]
            result_files = result.get("result_files", None)
            result_info = result.get("result_info", None)

            update_task_history_with_results(
                task_id,
                result_files=result_files,
                result_info=result_info
            )

        except TypeError:
            update_task_history_with_results(
                task_id,
                error=retval
            )

    def create_result_payload(self, progressbar_message, files=None, info=None):
        """Helper function for creating proper return dict.

        Passed arguments should be dictionaries.

        Args:
            progressbar_message (str): Message to display in the
                progress bar.
            files (dict of objs, optional): [description].
                Defaults to None.
            info ([type], optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """

        if files is not None:
            files = s3.upload_files(files, is_result=True, read_filename_from_file=True)

        result = {"result_files": files, "result_info": info}

        return {"progressbar_message": progressbar_message, "result": result}

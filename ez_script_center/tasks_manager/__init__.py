"""
Module for handling user defined tasks.

In __init__ of your app please import and initialize the
TaskManager object.
"""
from os.path import dirname, basename, join
from glob import glob
pwd = dirname(__file__)


class TasksManager:
    available_tasks = {}

    def __init__(self):
        for x in glob(join(pwd, '*.py')):
            if not basename(x).startswith('__') and basename(x) != "scripts":
                __import__(f"ez_script_center.tasks_manager.{basename(x)[:-3]}", globals(), locals())

    @staticmethod
    def register_task(url=None):
        # Make so that if URL is None, it makes the filename the url.

        def inner_func(task):
            TasksManager.__dict__["available_tasks"][url] = task
            return task

        return inner_func

"""
Module for handling user defined tasks.

In __init__ of your app please import and initialize the
TaskManager object.
"""
from os.path import basename, dirname, join
from glob import glob
pwd = dirname(__file__)
print(pwd)

AVAILABLE_TASKS = {}


def register_task(url):

    def inner_func(task):
        AVAILABLE_TASKS.update[url] = task
        return task

    return inner_func


for x in glob(join(pwd, '*.py')):
    if not x.startswith('__'):
        __import__(basename(x)[:-3], globals(), locals())

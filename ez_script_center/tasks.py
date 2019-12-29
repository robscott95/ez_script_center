from flask import Blueprint, render_template, redirect, url_for, jsonify
from . import celery_worker
import random
import time
import logging

from .tasks_manager import AVAILABLE_TASKS

tasks = Blueprint('tasks', __name__)

logger = logging.getLogger('celery_error')


@tasks.route('/status/<task_url>/<task_id>', methods=["GET"])
def task_status(task_url, task_id):

    task = AVAILABLE_TASKS[task_url].AsyncResult(task_id)

    try:
        task = task.get()

        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...'
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
        elif task.state == "SUCCESS":
            response = {
                'state': task.state,
                'current': task.info.get('current', 1),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', ''),
                'result': task.info['result']
            }
        else:
            # Anything unhandled
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'result': str(task.result)
            }

    except Exception:
        # If an error is raised when getting the results, just handle
        # it as a failed task.
        response = {
            'state': "FAILED",
            'current': 0,
            'total': 1,
            'status': "ERROR",
            'result': str(task.result)
        }

    task.forget()

    return jsonify(response)

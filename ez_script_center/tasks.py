from flask import Blueprint, render_template, redirect, url_for, jsonify, current_app
from . import celery_worker
import logging

from .tasks_manager import TasksManager

tasks = Blueprint('tasks', __name__)

logger = logging.getLogger('celery_error')


@tasks.route('/status/<task_url>/<task_id>', methods=["GET"])
def task_status(task_url, task_id):

    task = TasksManager.available_tasks[task_url].AsyncResult(task_id)

    try:
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

            task.forget()

        else:
            # Anything unhandled.
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': task.status,
            }

            if task.failed():
                response["result"] = str(task.result)
                task.forget()

    except Exception as e:
        # If an error is raised when getting the results, just handle
        # it as a failed task.
        current_app.logger.critical(f"{task_url}, ID:{task_id} failed because of {e}")

        response = {
            'state': "FAILED",
            'current': 0,
            'total': 1,
            'status': "ERROR",
            'result': e
        }

        task.forget()

    return jsonify(response)

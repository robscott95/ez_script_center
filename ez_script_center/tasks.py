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
                'progressbar_message': 'Pending...'
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'progressbar_message': task.info.get('progressbar_message', 'In progress...')
            }
        elif task.state == "SUCCESS":
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'progressbar_message': task.result.get('progressbar_message', 'Task done.'),
                'result': task.result['result']
            }

            task.forget()

        else:
            # Anything unhandled and failed tasks.
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'progressbar_message': task.info.get('progressbar_message', "No progress bar message")
            }

            if task.failed():
                current_app.logger.error(f"{task_url}, ID:{task_id} failed because of {task.result}")
                response["progressbar_message"] = str(task.result)
                task.forget()

    except Exception as e:
        # If an error is raised when getting the results, just handle
        # it as a failed task.
        current_app.logger.critical(f"{task_url}, ID:{task_id} failed because of {e}")

        response = {
            'state': "FAILURE",
            'current': 0,
            'total': 1,
            'progressbar_message': "CRITICAL ERROR, CHECK LOGS",
            'result': str(e)
        }

        task.forget()

    return jsonify(response)

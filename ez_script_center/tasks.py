from flask import Blueprint, render_template, redirect, url_for, jsonify, current_app
from . import celery_worker
import logging

from .tasks_manager import TasksManager
from .database_manager import get_task_history
from . import s3

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
                'result': task.result['result'],
                'result_url': url_for("tasks.task_result", task_id=task_id)
            }

            task.forget()

        else:
            # Anything unhandled and failed tasks.
            try:
                progressbar_message = task.info.get('progressbar_message', "No progress bar message")
            except KeyError:
                progressbar_message = str(task.result)

            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'progressbar_message': progressbar_message
            }

            if task.failed():
                current_app.logger.error(f"{task_url}, ID:{task_id} failed because of {task.result}")
                task.forget()

    except Exception as e:
        # If an error is raised when getting the results, just handle
        # it as a failed task.
        current_app.logger.critical(f"{task_url}, ID:{task_id} failed because of {e}")

        response = {
            'state': " ",
            'current': 0,
            'total': 1,
            'progressbar_message': "CRITICAL ERROR, CHECK LOGS",
            'result': str(e)
        }

        task.forget()

    return jsonify(response)


@tasks.route('/result/<task_id>', methods=["GET"])
def task_result(task_id):
    results = get_task_history(task_id)

    if results['input_files'] is not None:
        results['input_files'] = s3.generate_presigned_links(
            dict(results['input_files'])
        )

    if results['result_files'] is not None:
        results['result_files'] = s3.generate_presigned_links(
            dict(results['result_files'])
        )

    return jsonify(results)

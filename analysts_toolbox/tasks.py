from flask import Blueprint, render_template, redirect, url_for, jsonify
from . import celery
import random
import time
import logging

tasks = Blueprint('tasks', __name__)

logger = logging.getLogger('celery_error')


@tasks.route('/status/<task_id>', methods=["GET"])
def task_status(task_id):

    task = execute_ngram_analysis.AsyncResult(task_id)

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

# Scripts here are modified for celery usage.
from analysts_toolbox.scripts.ngram_analysis import execute_ngram_analysis


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(3, 5)
    for i in range(3):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}
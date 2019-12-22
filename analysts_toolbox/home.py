import json

from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user

from . import db
from . import auth as auth_blueprint

from .tasks import long_task, task_status

home = Blueprint('home', __name__)


@home.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('tools.menu'))


@home.route('/profile')
@login_required
def profile():
    user_info = auth_blueprint.get_user_info()
    return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"


@home.route('/long_task')
def longtask():
    task = long_task.apply_async()
    print(url_for('tasks._task_status', task_id=task.id))
    return jsonify({}), 202, {'Location': url_for('tasks._task_status',
                                                  task_id=task.id)}
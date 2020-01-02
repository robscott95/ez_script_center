"""Module that abstracts most useful database queries.
"""

from . import db
from .models import DataStorage, TaskHistory

from flask_login import current_user


def db_upload_task_request(user_id, input_info, input_files, tool_id):
    """Upload the data user has passed through the form and return
    the task id.

    Args:
        input_info ([type]): [description]
        input_files ([type]): [description]
        user_id ([type]): [description]
    """
    # Upload to db
    data_storage = DataStorage(
        user_id=user_id,
        input_info=input_info,
        input_files=list(input_files.items()),
    )

    task_history = TaskHistory(
        user_id=user_id,
        data_task_history=data_storage,
        tool_id=tool_id
    )

    db.session.add(task_history)
    db.session.flush()

    task_id = task_history.id

    db.session.commit()

    return task_id


def update_task_history_with_results(task_id, result_info=None, result_files=None, error=None):
    pass

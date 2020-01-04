"""Module that abstracts most useful database queries.
"""

from . import db
from .models import DataStorage, TaskHistory


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


def update_task_history_with_results(
    task_id,
    result_info=None,
    result_files=None,
    error=None
):
    # Get the user_id and data_storage_id
    task_history = TaskHistory.query.filter_by(id=task_id).first()
    data_storage = DataStorage.query.filter_by(id=task_history.task_data_id).first()

    # update data storage
    data_storage.result_info = result_info
    data_storage.result_files = list(result_files.items()) if result_files is not None else None
    data_storage.error = str(error)

    db.session.merge(data_storage)
    db.session.commit()

    return None

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    jsonify,
    Markup,
    request,
    current_app
)
from flask_login import login_required, current_user
from sqlalchemy.orm import load_only

from .models import TaskHistory
from . import s3

user = Blueprint("user", __name__, template_folder="templates/user")


@user.route('/history', methods=['GET'])
@login_required
def history():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    task_history = (
        TaskHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(TaskHistory.id.desc())
        .paginate(page, per_page, max_per_page=20, error_out=False)
    )

    task_history_content = [
        {
            "task_id": task.id,
            "tool_name": task.tools_task_history.name,
            "tool_url": task.tools_task_history.url,
            "input_info": task.data_task_history.input_info,
            "input_files": (
                s3.generate_presigned_links(dict(task.data_task_history.input_files))
                if task.data_task_history.input_files is not None else None
            ),
            "result_info": task.data_task_history.result_info if task.ready else {"Task info": "Not ready! Refresh for an update..."},
            "result_files": (
                s3.generate_presigned_links(dict(task.data_task_history.result_files))
                if task.data_task_history.result_files is not None else None
            ),
            "error": task.data_task_history.error,
            "ready": task.ready
        }
        for task in task_history.items
    ]

    # Add the pagination navigator under the table
    return render_template(
        "history.html",
        task_history_content=task_history_content,
        task_history=task_history
    )

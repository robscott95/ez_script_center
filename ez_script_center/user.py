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
from sqlalchemy.sql.expression import cast
from sqlalchemy import String as sql_string
from sqlalchemy.dialects import postgresql

from .models import TaskHistory, DataStorage, Tools
from . import s3

user = Blueprint("user", __name__, template_folder="templates/user")


@user.route('/history', methods=['GET'])
@login_required
def history():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Overall, I think it would be better to create a table for each
    # element and just reference it approprietly than to do this mental
    # gymnastics. One to many for data_input and data_files would be
    # sufficient.
    # This method of simple ilike is sufficient with current database
    # design, but if we want something more complex, then it'd be easier
    # to have a simpler database.

    def create_filter(value, query):
        filter_val = request.args.get(value, '')

        if filter_val == '':
            return None

        filter_val = filter_val.replace(' ', '%')

        return TaskHistory.data_task_history.has(query(f'%{filter_val}%'))

    filter_fields_and_queries = {
        "tool_name": Tools.name.ilike,
        "input_info": cast(DataStorage.input_info, sql_string).ilike,
        "input_file": cast(DataStorage.input_files, sql_string).ilike,
        "result_info": cast(DataStorage.result_info, sql_string).ilike,
        "result_file": cast(DataStorage.result_files, sql_string).ilike,
        "error": DataStorage.error.ilike
    }

    filters = [
        create_filter(value, query)
        for value, query in filter_fields_and_queries.items() 
        if create_filter(value, query) is not None
    ]

    task_history = (
        TaskHistory.query
        .filter(*filters)
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
                s3.generate_presigned_links(task.data_task_history.input_files)
                if task.data_task_history.input_files is not None else None
            ),
            "result_info": (
                task.data_task_history.result_info
                if task.ready else {"Task info": "Not ready! Refresh for an update..."}
            ),
            "result_files": (
                s3.generate_presigned_links(task.data_task_history.result_files)
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

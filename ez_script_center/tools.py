from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    jsonify,
    Markup,
    request,
    current_app,
    make_response
)
from flask_login import login_required, current_user

from .database_manager import db_upload_task_request
from .models import Tools

from .tasks_manager import TasksManager
from . import s3

tools = Blueprint("tools", __name__, template_folder="templates/tool_templates")


@tools.route("/menu")
@login_required
def menu():
    available_tools = Tools.query.all()
    available_tools = [
        [tool_info.name, tool_info.short_description, tool_info.url]
        for tool_info in available_tools
        if tool_info.visible
        and not tool_info.min_req_access_level > current_user.access_level
    ]

    return render_template("menu.html", items=available_tools)


@tools.route("/<tool_url>", methods=["GET", "POST"])
@login_required
def specific_tool(tool_url):
    # Availability check
    tool_info = Tools.query.filter_by(url=tool_url).first()
    if tool_info is None:
        return "No such script available", 404

    elif not tool_info.visible:
        return f"{tool_info.name} is currently unavailable.", 404

    elif tool_info.min_req_access_level > current_user.access_level:
        current_app.logger.warning(f"User {current_user.id} attempted to access {tool_url}.")
        return "Access denied. This attempt is logged.", 403

    elif tool_url not in TasksManager.available_tasks:
        current_app.logger.error(
            f"{tool_url} wasn't found in available tasks. Check the url of registered task (if None, fix the filename)."
        )
        return (f"{tool_url} wasn't found in available tasks. Check the url of registered task (if None, "
                f"fix the filename).", 500)

    form_custom_template = TasksManager.available_forms[tool_url]["custom_template"]
    wtf_form = TasksManager.available_forms[tool_url]["form_data"]()

    if request.method == "GET":
        tool_desc = Markup(tool_info.long_description)
        tool_instructions = Markup(tool_info.instructions) if tool_info.instructions is not None else None

        if not form_custom_template:
            return render_template("wtforms_template_rendering.html",
                                   long_desc=tool_desc,
                                   tool_name=tool_info.name,
                                   tool_instructions=tool_instructions,
                                   form_data=wtf_form)
        else:
            return render_template(f"{tool_url}.html",
                                   long_desc=tool_desc,
                                   tool_name=tool_info.name,
                                   tool_instructions=tool_instructions,
                                   form_data=wtf_form)

    if request.method == "POST":
        if not wtf_form.validate_on_submit():
            form_errors = {ele.name: ele.errors[0] for ele in wtf_form if ele.errors}
            return jsonify(form_errors), 200, {'form_validation_error': True}

        input_info = {key: value for key, value in request.form.items() if key != 'csrf_token'}
        input_files = s3.upload_files(request.files, read_filename_from_file=True)

        task_id = db_upload_task_request(current_user.id, input_info,
                                         input_files, tool_info.id)

        # Create a data object to pass on to the task
        data = {"input_files": input_files,
                "input_info": input_info}

        task = TasksManager.available_tasks[tool_url].apply_async(args=(data,),
                                                                  task_id=str(task_id))

        return (
            jsonify({}),
            202,
            {"task_status_url": url_for("tasks.task_status", task_url=tool_url, task_id=task.id),
             "form_validation_error": False}
        )

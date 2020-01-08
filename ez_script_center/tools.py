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
from flask_wtf import FlaskForm

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
    if not tool_info.visible:
        return f"{tool_info.name} is currently unavailable.", 404

    if tool_info.min_req_access_level > current_user.access_level:
        current_app.logger.warning(f"User {current_user.id} attempted to access {tool_url}.")
        return "Access denied. This attempt is logged.", 403

    if TasksManager.available_tasks.get(tool_url, None) is None:
        current_app.logger.error(f"{tool_url} wasn't found in available tasks. Check the url of registered task (if None, fix the filename).")
        return f"{tool_url} wasn't found in available tasks. Check the url of registered task (if None, fix the filename).", 500

    if request.method == "GET":
        tool_desc = Markup(tool_info.long_description)

        return render_template(f"{tool_url}.html", long_desc=tool_desc)

    if request.method == "POST":
        # TODO jak jest odczytanie pliku DONE
        # Przesyłanie temp plików do jakieś s3 DONE
        # Klasa do zarzadzania zapisywania i odbioru plikow z s3 DONE
        # rezultatowe pliki takze DONE
        # Handle the tasks.py better. Check for raising erros behaviour DONE
        # Upload automatyczny do bazy/updejt w przypadku zwracania rezultatow DONE
        # Download przy rezultacie DONE
        # user privilages (read and read+write) DONE
        # wtforms
        # sprawdzenie jak to przepuscic do kodu
        # danie restrykcji na poziomie template'a htmlowego
        # historia

        # TODO: do for multiple files

        input_info = request.form
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
            {"task_status_url": url_for(
                "tasks.task_status", task_url=tool_url, task_id=task.id
            )},
        )

from flask import Blueprint, render_template, redirect, url_for, jsonify, Markup, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from . import db
from .models import Tools, FileStorage
from . import tasks
from .tasks_manager import available_tasks
from . import s3

tools = Blueprint('tools', __name__, template_folder="templates/tool_templates")


@tools.route("/menu")
@login_required
def menu():
    available_tools = Tools.query.all()
    available_tools = [
        [tool_info.name, tool_info.short_description, tool_info.url]
        for tool_info in available_tools if tool_info.visible
    ]

    print(available_tools)
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

    if request.method == "GET":
        tool_desc = Markup(tool_info.long_description)

        return render_template(f"{tool_url}.html",
                               long_desc=tool_desc)

    if request.method == "POST":
        # TODO jak jest odczytanie pliku DONE
        # Przesyłanie temp plików do jakieś s3 DONE
        # Klasa do zarzadzania zapisywania i odbioru plikow z s3 DONE
        # rezultatowe pliki takze DONE
        # wtforms
        # sprawdzenie jak to przepuscic do kodu
        # danie restrykcji na poziomie template'a htmlowego
        # historia

        # Upload file to temp storage.
        # TODO: do for multiple files

        # tool_manager = ToolManager()
        # tool_manager.exec(tool_url)
        # tool_manager has to contain 

        s3_links = s3.upload_files(request.files.values())
        print(s3_links)

        # Upload to db for safekeeping
        file_storage = FileStorage(
            user_id=current_user.id,
            input_info="none",
            input_files_url=list(s3_links)
        )
        db.session.add(file_storage)
        db.session.commit()

        # Do the task.
        task = available_tasks[tool_url].apply_async(args=(data, ))

        print(url_for('tasks.task_status', task_id=task.id))
        return jsonify({}), 202, {'Location': url_for('tasks.task_status',
                                                      task_id=task.id)}

        
# @tools.route("/n-gram-analysis", methods=["GET", "POST"])
# @login_required
# def n_gram_analysis():
#     if request.method == "GET":
#         n_gram_analysis = Tools.query \
#             .filter_by(name="N-gram Analysis") \
#             .first()

#         tool_desc = Markup(n_gram_analysis.long_description)

#         return render_template(
#             "n-gram-analysis.html",
#             long_desc=tool_desc
#         )
#     if request.method == "POST":
#         # TODO jak jest odczytanie pliku DONE
#         # Przesyłanie temp plików do jakieś s3 DONE
#         # Klasa do zarzadzania zapisywania i odbioru plikow z s3 DONE
#         # rezultatowe pliki takze DONE
#         # wtforms
#         # sprawdzenie jak to przepuscic do kodu
#         # danie restrykcji na poziomie template'a htmlowego
#         # historia

#         # Upload file to temp storage.
#         # TODO: do for multiple files

#         s3_links = s3.upload_files(request.files.values())
#         print(s3_links)

#         # Upload to db for safekeeping
#         file_storage = FileStorage(
#             user_id=current_user.id,
#             input_info="none",
#             input_files_url=list(s3_links)
#         )
#         db.session.add(file_storage)
#         db.session.commit()

#         # Do the task.
#         task = tasks.execute_ngram_analysis.apply_async(args=(str(data),), 
#                                                         serializer="json")
#         print(url_for('tasks.task_status', task_id=task.id))
#         return jsonify({}), 202, {'Location': url_for('tasks.task_status',
#                                                       task_id=task.id)}


# @tools.route('/longtask', methods=['POST'])
# def longtask():
#     task = tasks.long_task.apply_async()
#     print(url_for('tasks.task_status', task_id=task.id))
#     return jsonify({}), 202, {'Location': url_for('tasks.task_status',
#                                                   task_id=task.id)}

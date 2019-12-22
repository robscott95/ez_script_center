from flask import Blueprint, render_template, redirect, url_for, jsonify, Markup, request
from flask_login import login_required, current_user
import pickle, csv, json

from . import db
from .models import Tools, TempStorage
from . import tasks

tools = Blueprint('tools', __name__, template_folder="templates/tool_templates")


@tools.route("/menu")
@login_required
def menu():
    available_tools = Tools.query.all()
    available_tools = [
        [tool_info.name, tool_info.short_description, "-".join(tool_info.name.lower().split())]
        for tool_info in available_tools
    ]

    print(available_tools)
    return render_template("menu.html", items=available_tools)


@tools.route("/n-gram-analysis", methods=["GET", "POST"])
@login_required
def n_gram_analysis():
    if request.method == "GET":
        n_gram_analysis = Tools.query \
            .filter_by(name="N-gram Analysis") \
            .first()

        tool_desc = Markup(n_gram_analysis.long_description)

        return render_template(
            "n-gram-analysis.html",
            long_desc=tool_desc
        )
    if request.method == "POST":
        # Działa
        # TODO jak jest odczytanie pliku DONE
        # Przesyłanie temp plików do jakieś s3 czy cuś
        # rezultatowe pliki takze
        # wtforms
        # sprawdzenie jak to przepuscic do kodu
        # danie restrykcji na poziomie template'a htmlowego
        # historia
        print(request.form)
        # print(request.files["input_data"].read())
        data = request.files["input_data"].read()
        print(data)
        # print(type(request.files["input_data"].read()))
        # print(pd.read_csv(request.files["data"]))
        # task = tasks.long_task.apply_async()

        # Upload file to temp storage.
        # TODO: do for multiple files

        task = tasks.execute_ngram_analysis.apply_async(args=(str(data),), serializer="pickle")
        print(url_for('tasks.task_status', task_id=task.id))
        return jsonify({}), 202, {'Location': url_for('tasks.task_status',
                                                      task_id=task.id)}


@tools.route('/longtask', methods=['POST'])
def longtask():
    task = tasks.long_task.apply_async()
    print(url_for('tasks.task_status', task_id=task.id))
    return jsonify({}), 202, {'Location': url_for('tasks.task_status',
                                                  task_id=task.id)}

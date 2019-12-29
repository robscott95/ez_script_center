from flask_login import UserMixin
from sqlalchemy.dialects import postgresql
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(1000))
    data_stored_id = db.relationship("FileStorage", backref='file_storage', lazy=True)
    task_history_id = db.relationship("TaskHistory", backref="task_history", lazy=True)


class Tools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), nullable=False, unique=True)
    visible = db.Column(db.Boolean, nullable=False, default=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    short_description = db.Column(db.Text())
    long_description = db.Column(db.Text())
    json_settings = db.Column(db.Text())


class DataStorage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    input_info = db.Column(db.JSON)
    input_files_url = db.Column(postgresql.ARRAY(db.String))
    result_info = db.Column(db.JSON)
    result_files_url = db.Column(postgresql.ARRAY(db.String))
    task_history_id = db.relationship 

class TaskHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    task_data_id = db.Column(db.Integer, db.ForeignKey("data_storage.id"), nullable=False)
    tool_id =  db.Column(db.Integer, db.ForeignKey("tools.id", nullable=False))


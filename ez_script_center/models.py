from flask_login import UserMixin
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import backref
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(1000))
    # Access levels
    # 0 - can't access anything
    # 1 - basic access privilage
    # 2 - elevated access privilage (for example: to allow executing modifying scripts)
    access_level = db.Column(db.SmallInteger(), nullable=False, default=1)
    task_history = db.relationship("TaskHistory", backref="user_task_history", lazy=True)


class Tools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), nullable=False, unique=True)
    visible = db.Column(db.Boolean(), nullable=False, default=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    short_description = db.Column(db.Text())
    long_description = db.Column(db.Text())
    min_req_access_level = db.Column(db.SmallInteger(), nullable=False, default=1)
    task_history = db.relationship("TaskHistory", backref="tools_task_history", lazy=True)


class DataStorage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    input_info = db.Column(db.JSON())
    input_files = db.Column(postgresql.ARRAY(db.String))
    result_info = db.Column(db.JSON())
    result_files = db.Column(postgresql.ARRAY(db.String))
    error = db.Column(db.Text())
    task_history = db.relationship("TaskHistory",
                                   backref=backref("data_task_history", uselist=False))


class TaskHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    task_data_id = db.Column(db.Integer, db.ForeignKey("data_storage.id"))
    tool_id = db.Column(db.Integer, db.ForeignKey("tools.id"))

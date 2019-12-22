from flask_login import UserMixin
from sqlalchemy.dialects import postgresql
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(1000))
    results = db.relationship("ResultStorage")

class Tools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    short_description = db.Column(db.Text())
    long_description = db.Column(db.Text())
    json_settings = db.Column(db.Text())

class TempStorage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    temp_files_url = db.Column(postgresql.ARRAY(db.String))

class ResultStorage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    input_info = db.Column(db.JSON)
    input_files_url = db.Column(postgresql.ARRAY(db.String))
    result_info = db.Column(db.JSON)
    result_files_url = db.Column(postgresql.ARRAY(db.String))

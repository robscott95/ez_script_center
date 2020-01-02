import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from celery import Celery

from oauthlib.oauth2 import WebApplicationClient

from . import config as c
from .s3_file_manager import S3Manager
from .tasks_manager import TasksManager

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
celery_worker = Celery(__name__, broker=c.CELERY_BROKER_URL, backend=c.CELERY_BROKER_URL)

# init the oauth
oauth_client = WebApplicationClient(c.GOOGLE_CLIENT_ID)

# Get the s3 file handler
s3 = S3Manager(c.S3_BUCKET)

# Initialize TasksManager so it can read and add all the available
# tasks from tasks_manager package.
TasksManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = c.APP_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = c.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "You need to login to be able to view that page. Please do so."
    login_manager.session_protection = "basic"
    login_manager.init_app(app)

    # Celery conf
    celery_worker.conf.update(app.config)
    celery_worker.conf["CELERY_ACCEPT_CONTENT"] = c.CELERY_ACCEPT_CONTENT
    celery_worker.conf["CELERYD_TASK_SOFT_TIME_LIMIT"] = c.CELERYD_TASK_SOFT_TIME_LIMIT

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user
        # table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .tools import tools as tools_blueprint
    app.register_blueprint(tools_blueprint, url_prefix="/tools")

    from .tasks import tasks as tasks_blueprint
    app.register_blueprint(tasks_blueprint, url_prefix="/tasks")

    return app


app = create_app()
app.app_context().push()

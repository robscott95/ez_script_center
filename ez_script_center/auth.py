import functools
import requests
import json

from flask import Blueprint, render_template, redirect, url_for, request, session, make_response
from flask_login import login_user, login_required, logout_user, current_user

from .models import User
from . import db
from . import config as c
from . import oauth_client

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=["GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    request_uri = oauth_client.prepare_request_uri(
        c.GOOGLE_AUTH_ENDPOINT,
        redirect_uri=c.GOOGLE_AUTH_REDIRECT_URI,
        scope=c.AUTHORIZATION_SCOPE
    )

    return redirect(request_uri)


@auth.route('/google/auth')
def google_auth_redirect():

    if "error" in request.args:
        response = make_response('Error occured, check logs', 401)
        return response

    code = request.args.get('code', default=None, type=None)

    if code is None:
        return redirect(url_for('auth.login'))

    token_url, headers, body = oauth_client.prepare_token_request(
        c.ACCESS_TOKEN_URI,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(c.GOOGLE_CLIENT_ID, c.GOOGLE_CLIENT_SECRET)
    )

    oauth_client.parse_request_body_response(json.dumps(token_response.json()))

    uri, headers, body = oauth_client.add_token(c.GOOGLE_USERINFO_ENDPOINT)

    user_info = requests.get(uri, headers=headers, data=body).json()

    user = User.query.filter_by(email=user_info["email"]).first()

    # If no user was found, create him.
    if not user:
        user = User(
            email=user_info["email"], name=user_info["given_name"]
        )

        # add the new user to the database
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    print(f"Auth Log: {user.email} logged in.")
    return redirect(url_for('home.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for('auth.login'))

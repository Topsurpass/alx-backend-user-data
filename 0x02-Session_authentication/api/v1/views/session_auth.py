#!/usr/bin/env python3
"""Handles all routes for the Session authentication."""

from flask import abort, jsonify, request
from typing import Tuple
from models.user import User
from api.v1.views import app_views
import os


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def login_user() -> str:
    """login user and create new session id for the user"""
    err = {
            'no_email': {"error": "email missing"},
            'no_password': {"error": "password missing"},
            'no_user_found': {"error": "no user found for this email"},
            'wrong_password': {"error": "wrong password"}
        }
    if not request.form.get('email'):
        return jsonify(err.get('no_email')), 400
    if not request.form.get('password'):
        return jsonify(err.get('no_password')), 400
    try:
        users = User.search({'email': request.form.get('email')})
    except Exception:
        return jsonify(err.get('no_user_found')), 404
    if len(users) <= 0:
        return jsonify(err.get('no_user_found')), 404
    if users[0].is_valid_password(request.form.get('password')):
        from api.v1.app import auth
        session_id = auth.create_session(getattr(users[0], 'id'))
        user_dict = jsonify(users[0].to_json())
        user_dict.set_cookie(os.getenv("SESSION_NAME"), session_id)
        return user_dict
    return jsonify(err.get('wrong_password')), 401


@app_views.route(
        '/auth_session/logout', methods=['DELETE'], strict_slashes=False)
def logout() -> (str, int):
    """Log a user out and deletes session id"""
    from api.v1.app import auth
    is_logged_out = auth.destroy_session(request)
    if is_logged_out:
        return jsonify({}), 200
    else:
        abort(404)

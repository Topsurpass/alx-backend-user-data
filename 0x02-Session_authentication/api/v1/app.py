#!/usr/bin/env python3
"""
Route module for the API
"""
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)
from api.v1.auth.auth import Auth
from api.v1.auth.basic_auth import BasicAuth
from api.v1.auth.session_auth import SessionAuth
from api.v1.auth.session_exp_auth import SessionExpAuth
from api.v1.auth.session_db_auth import SessionDBAuth
import os


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
auth = None

"""Determine type of authentication to use with default
being auth"""
auth_type = os.getenv('AUTH_TYPE', 'auth')
if auth_type == 'auth':
    auth = Auth()
if auth_type == 'basic_auth':
    auth = BasicAuth()
if auth_type == 'session_auth':
    auth = SessionAuth()
if auth_type == 'session_exp_auth':
    auth = SessionExpAuth()
if auth_type == 'session_db_auth':
    auth = SessionDBAuth()


@app.errorhandler(404)
def not_found(error) -> str:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unathorized_request(error) -> str:
    """Unathorized request"""
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def no_access_to_res(error) -> str:
    """Authenticated but not allowed to a resource"""
    return jsonify({"error": "Forbidden"}), 403


@app.before_request
def authenticate_request():
    """Filter each reques but this is done before every
    blueprinted request/route/endpoint"""
    # List of endpoints that does not require authentication
    # before its access
    excluded_end_point = [
            '/api/v1/status/',
            '/api/v1/unauthorized/',
            '/api/v1/forbidden/',
            '/api/v1/auth_session/login/'
            ]
    if auth is not None:
        """If the request requires authorization"""
        if auth.require_auth(request.path, excluded_end_point):
            """Get the authentication credential"""
            auth_header = auth.authorization_header(request)
            user = auth.current_user(request)
            if auth_header is None and \
                    auth.session_cookie(request) is None:
                abort(401)
            if user is None:
                abort(403)
            request.current_user = user


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = os.getenv("API_PORT", "5000")
    app.run(host=host, port=port)

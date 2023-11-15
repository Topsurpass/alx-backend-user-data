#!/usr/bin/env python3
"""This module contains basic flask app set up"""

from flask import Flask, jsonify, request, abort, redirect
from auth import Auth


AUTH = Auth()
app = Flask(__name__)


@app.route('/', methods=['GET'], strict_slashes=False)
def home_page():
    """Endpoint fo accessing homepage and it
    returns a JSON payload of form"""

    return jsonify({"message": "Bienvenue"}), 200


@app.route("/users", methods=["POST"], strict_slashes=False)
def create_new_user():
    """Endpoint for creating new user"""
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=['POST'], strict_slashes=False)
def login():
    """Login user"""
    email = request.form.get("email")
    password = request.form.get("password")
    valid_user = AUTH.valid_login(email, password)
    if not valid_user:
        abort(401)
    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    """Cookie set to client browser as session_id after successful
    login"""
    response.set_cookie("session_id", session_id)
    return response


@app.route("/sessions", methods=["DELETE"], strict_slashes=False)
def logout():
    """Log user out of the app"""
    """Get cookie from client browser with the name session_id"""
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if not user:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect("/")


@app.route("/profile", methods=["GET"], strict_slashes=False)
def profile():
    """Use session_id to find a user"""
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email}), 200
    abort(403)


@app.route("/reset_password", methods=["POST"], strict_slashes=False)
def reset_password():
    """Reset user password"""
    email = request.form.get("email")
    new_token = None
    try:
        new_token = AUTH.get_reset_password_token(email)
    except ValueError:
        new_token = None
    if new_token is None:
        abort(403)
    return jsonify({"email": email, "reset_token": new_token})


@app.route("/reset_password", methods=["PUT"], strict_slashes=False)
def update_password():
    """Endpoint for updating user password"""
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    is_password_updated = False
    try:
        AUTH.update_password(reset_token, new_password)
        is_password_updated = True
    except ValueError:
        is_password_updated = False
    if not is_password_updated:
        abort(403)
    return jsonify({"email": email, "message": "Password updated"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")

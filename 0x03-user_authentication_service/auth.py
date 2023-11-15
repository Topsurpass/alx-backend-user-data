#!/usr/bin/env python3
"""This module takes care of the user authenthecation"""

import bcrypt
from db import DB
from typing import TypeVar
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4
from typing import TypeVar, Union


def _hash_password(password: str) -> bytes:
    """Hash password using bcrypt and return the salted hash"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """validate that the provided password matches the
    hashed password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def _generate_uuid():
    """Generate unique id"""
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """
    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register user and save to the database"""
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))
        raise ValueError('User {} already exists'.format(email))

    def valid_login(self, email: str, password: str) -> bool:
        """Validate password before login"""
        try:
            user = self._db.find_user_by(email=email)
            return is_valid(user.hashed_password, password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """Create session ID"""
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None
        if user:
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        else:
            return None

    def get_user_from_session_id(
            self, session_id: str) -> Union[User, None]:
        """Try get a user using session id rather than
        needing to input email and password for reverification"""
        if not session_id:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None
        return user

    def destroy_session(self, user_id: int) -> None:
        """Destroy session ID of a user. Useful when a user logout"""
        if not user_id:
            return None
        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """Reset password token and generate new one.
        Add to the reset_tokee of the User attribute"""
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            user = None
        if not user:
            raise ValueError
        new_token = _generate_uuid()
        self._db.update_user(user.id, reset_token=new_token)
        return new_token

    def update_password(self,  reset_token: str, password: str) -> None:
        """Update user password and delete the reset_token
        used for updating the password"""
        user = None
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            user = None
        if not user:
            raise ValueError()
        new_password = _hash_password(password)
        self._db.update_user(user.id, hashed_password=new_password,
                             reset_token=None)
        return None

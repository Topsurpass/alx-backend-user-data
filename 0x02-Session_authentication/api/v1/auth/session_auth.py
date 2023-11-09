#!/usr/bin/env python3
"""This module contains the creation of new authentication mechanism"""
from api.v1.auth.auth import Auth
from models.user import User
import uuid


class SessionAuth(Auth):
    """Authentication mechanism using session auth"""
    user_id_by_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """Create session id for a user_id"""
        if user_id:
            if type(user_id) is str:
                s_id = str(uuid.uuid4())
                """key = session_id, value = user_id; This is
                done so that a user can have multiple session id"""
                self.user_id_by_session_id[s_id] = user_id
                return s_id
            else:
                None
        return None

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """Return User ID based on Session ID"""
        if session_id:
            if type(session_id) is str:
                return self.user_id_by_session_id.get(session_id)
            else:
                return None
        return None

    def current_user(self, request=None):
        """Return User instance based on a cookie value"""
        session_id = self.session_cookie(request)
        user_id = self.user_id_for_session_id(session_id)
        return User.get(user_id)

    def destroy_session(self, request=None):
        """Deletes the user session / logout"""
        session_id = self.session_cookie(request)
        user_id = self.user_id_for_session_id(session_id)
        if request is None or session_id is None or user_id is None:
            return False
        if session_id in self.user_id_by_session_id:
            del self.user_id_by_session_id[session_id]
        return True

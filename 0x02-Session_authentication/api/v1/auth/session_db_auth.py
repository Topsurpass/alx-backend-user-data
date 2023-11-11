#!/usr/bin/env python3
"""This module contains the new authorization system
stored in the database, in a file storage in this case"""
from api.v1.auth.session_exp_auth import SessionExpAuth
from models.user_session import UserSession
from flask import request
from datetime import datetime, timedelta


class SessionDBAuth(SessionExpAuth):
    """Class for new authorization system stored in db
    with expiration time"""
    def create_session(self, user_id=None) -> str:
        """Overloads this is in base class. Create and store
        a session id in db for the user"""
        session_id = super().create_session(user_id)
        if type(session_id) is str:
            dic = {
                    'user_id': user_id,
                    'session_id': session_id
                }
            new_user = UserSession(**dic)
            new_user.save()
            return session_id

    def user_id_for_session_id(self, session_id=None):
        """Overloads this in the base class. Search the db for User ID
        using the session_id"""
        try:
            session_dic = UserSession.search({'session_id': session_id})
        except Exception:
            return None
        """Set expiration time by adding more seconds/minutes
        to the created time from shell env"""
        if len(session_dic) <= 0:
            return None
        curr_time = datetime.now()
        t_span = timedelta(seconds=self.session_duration)
        exp_time = session_dic[0].created_at + t_span
        if exp_time < curr_time:
            return None
        return session_dic[0].user_id

    def destroy_session(self, request=None) -> bool:
        """Destroys UserSession from db based on Session ID from
        request cookie"""
        session_id = self.session_cookie(request)
        try:
            sessions = UserSession.search({'session_id': session_id})
        except Exception:
            return False
        if len(sessions) <= 0:
            return False
        sessions[0].remove()
        return True

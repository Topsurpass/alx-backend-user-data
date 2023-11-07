#!/usr/bin/env python3
"""This module handles the basic authentication of our API"""

from flask import request
from typing import TypeVar, List
import fnmatch


class Auth:
    """This class handles our authentication system"""

    def __init__(self):
        """Initialize class instance"""
        pass

    def require_auth(
            self, path: str, excluded_paths: List[str]) -> bool:
        """The function that helps specify which route/path
        requires authentication and ones that does not"""
        if path is None or excluded_paths is None or \
                len(excluded_paths) == 0:
            return True
        r_path = path.rstrip('/')
        for ex_path in excluded_paths:
            ex_path = ex_path.rstrip('/')
            if fnmatch.fnmatch(r_path, ex_path):
                return False
        return True

    def authorization_header(self, request=None) -> str:
        """This handles the authentication credentials
        in http header"""
        auth = request.headers.get('Authorization') if request \
            is not None else None
        if request is None or auth is None:
            return None
        else:
            return auth

    def current_user(self, request=None) -> TypeVar('User'):
        """return object of class User"""
        return None

#!/usr/bin/env python3
"""This module a new model for new authentication
system"""
from models.base import Base


class UserSession(Base):
    """New model for new authentication system"""
    def __init__(self, *args: list, **kwargs: dict):
        """Initialize class instance/object with base class args"""
        super().__init__(*args, **kwargs)
        self.user_id = kwargs.get('user_id')
        self.session = kwargs.get('session_id')

#!/usr/bin/env python3
"""This module contains function that hashed sensitive
information / data before being stored in database"""

import bcrypt


def hash_password(password: str) -> bytes:
    """Hash password and return hashed hashed password
    string"""
    """"Hash a password for the first time, with a
    randomly-generated salt"""
    return bcrypt.hashpw(password.encode('utf-8'), bycrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """validate that the provided password matches the
    hashed password"""

    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

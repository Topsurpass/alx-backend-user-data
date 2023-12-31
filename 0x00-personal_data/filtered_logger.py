#!/usr/bin/env python3
"""This module contains methods of keeping personal
information safe and also encryption of them before storage"""

from typing import List
import logging
import os
import mysql.connector
import re

patterns = {
    'extract': lambda x, y: r'(?P<field>{})=[^{}]*'.format('|'.join(x), y),
    'replace': lambda x: r'\g<field>={}'.format(x),
}
PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
        fields: List[str], redaction: str, message: str, separator: str,
        ) -> str:
    """return log messages obfuscated"""
    extract, replace = (patterns["extract"], patterns["replace"])
    return re.sub(extract(fields, separator), replace(redaction), message)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class"""
    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """Initialize the instance with logging.Formatter"""
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """filter values in incoming log records"""
        message = super(RedactingFormatter, self).format(record)
        return filter_datum(
                self.fields, self.REDACTION, message, self.SEPARATOR)


def get_logger() -> logging.Logger:
    """Create new customized logger i.e logging.Logger object"""
    newLogger = logging.getLogger("user_data")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    newLogger.setLevel(logging.INFO)
    newLogger.propagate = False
    newLogger.addHandler(stream_handler)
    return newLogger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Connect to database and return its connector"""
    db_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.getenv("PERSONAL_DATA_DB_NAME", "")
    db_user = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    db_pass = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")

    connection = mysql.connector.connect(
            host=db_host,
            port=3306,
            user=db_user,
            password=db_pass,
            database=db_name
    )
    return connection


def main() -> None:
    """connect to db, retrieve all rows and display
    each row under a filtered format"""
    filtered_fields = "name,email,phone,ssn,password,ip,last_login,user_agent"
    cols = filtered_fields.split(',')
    sqlQuery = f'SELECT {filtered_fields} FROM users;'
    logger = get_logger()
    db_connect = get_db()
    with db_connect.cursor() as cursor:
        cursor.execute(sqlQuery)
        rows = cursor.fetchall()
        for row in rows:
            eachRecord = map(
                    lambda x: f'{x[0]}={x[1]}', zip(cols, row))
            msg = '{};'.format('; '.join(list(eachRecord)))
            args = ("user_data", logging.INFO, None, None, msg, None, None)
            log_record = logging.LogRecord(*args)
            logger.handle(log_record)


if __name__ == '__main__':
    main()

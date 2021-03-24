"""Filename: rel_database

Description: CRUD functions to interact with a database, offer the following methods:
-

USAGE
-----
$ python cvp/data/rel_database.py

"""

# Standard Dist
import logging
import os
import sqlite3
import sys
import coloredlogs

# Third party imports
from sqlite3 import Error
from pathlib import Path
from sqlalchemy import create_engine

# Project Level Imports

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)


class Database:
    """ Database instance for CRUD interaction
    """

    def __init__(self, db_path):
        """ construct the database
        :param db_path: path to the database
        """
        Path(db_path).touch()
        self.conn = self.create_connection(db_path)
        self.engine = create_engine('sqlite:///' + db_path, echo=False)
        self.cursor = self.conn.cursor()


    def create_connection(self, db_path):
        """ create a db connection to database
        :param db_path: database file path
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_path)
            logger.info('SUCCESS: Connected to Database')
            return conn
        except Error as e:
            logger.debug(e)

        return None

    def close_connection(self):
        """ close the connection
        """
        if self.conn != None:
            self.conn.close()

        if self.engine != None:
            self.engine.dispose()

    def insert(self, values: tuple, talbe_name: str):
        SQL_Insert = f'''INSERT INTO {talbe_name} VALUES (?,?,?,?,?,?)'''

        self.cursor.execute(SQL_Insert, values)
        logger.info(f'SUCCESS: Insert into {talbe_name} successfully!')


def create_db(db_path: str, table_name: str, attr: dict):
    logger.info("")
    db = Database(db_path)

    SQL_CreateTable = f'''CREATE TABLE IF NOT EXISTS {table_name} ('''
    for key, value in attr.items():
        SQL_CreateTable += f'''\n{key} {value},'''
    SQL_CreateTable = SQL_CreateTable[:-1] + '''\n)'''

    db.cursor.execute(SQL_CreateTable)
    logger.info(f'SUCCESS: Table `{table_name}` Created')

    values = (1, 1, 'test', 'test', 'I', 'June 27, 2021')

    db.insert(values, 'profile')


if __name__ == "__main__":
    db_path = 'dataset/external/cvp.db'
    name = 'profile'
    attr = {
        'userID': 'INTEGER NOT NULL PRIMARY KEY',
        'patient_num': 'INTEGER NOT NULL',
        'last_name': 'VARCHAR NOT NULL',
        'first_name': 'VARCHAR NOT NULL',
        'middle_initial': 'CHAR(1)',
        'dob': 'VARCHAR NOT NULL'
    }

    create_db(db_path, name, attr)
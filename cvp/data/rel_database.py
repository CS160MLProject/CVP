"""Filename: rel_database

Description: CRUD functions to interact with a database, offer the following methods:
- create_connection
- close_connection
- create_table
- insert
- select
- update
- delete

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

        logger.info('SUCCESS: Connection Closed')

    def create_table(self, attr: dict, table_name: str):
        SQL_CreateTable = f'''CREATE TABLE IF NOT EXISTS {table_name} ('''
        for key, value in attr.items():
            SQL_CreateTable += f'''\n{key} {value},'''
        SQL_CreateTable = SQL_CreateTable[:-1] + '''\n)'''

        try:
            self.cursor.execute(SQL_CreateTable)
            logger.info(f'SUCCESS: Table `{table_name}` Created')
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)

    def insert(self, values: tuple, talbe_name: str):
        SQL_Insert = f'''INSERT INTO {talbe_name} VALUES (?,?,?,?,?,?)'''
        try:
            self.cursor.execute(SQL_Insert, values)
            self.conn.commit()
            logger.info(f'SUCCESS: Insert into `{talbe_name}` successfully!')
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)

    def select(self, values: str, table_name: str, priority: str = None, condition=False):
        SQL_Select = f'''SELECT {values} FROM {table_name}'''

        if condition:
            SQL_Select += f''' WHERE {priority}'''

        try:
            self.cursor.execute(SQL_Select)
            result = self.cursor.fetchall()
            logger.info('SUCCESS: Selection successfully!')

            return result
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)

    def update(self, values: tuple, table_name: str, table_col: tuple, priority: str):
        SQL_Update = f'''UPDATE {table_name} SET '''
        for col in table_col:
            SQL_Update += f'''{col} = ?, '''
        SQL_Update = SQL_Update[:-2] + f''' WHERE {priority}'''

        logger.debug(SQL_Update)
        try:
            self.cursor.execute(SQL_Update, values)
            self.conn.commit()
            logger.info(f'SUCCESS: Update `{table_name}` successfully!')
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)

    def delete(self, table_name: str, priority: str):
        SQL_Delete = f'''DELETE FROM {table_name} WHERE {priority}'''

        try:
            self.cursor.execute(SQL_Delete)
            self.conn.commit()
            logger.info(f'SUCCESS: Delete `{priority}` in `{table_name}` successfully!')
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)


"""
def test_db(db_path: str, table_name: str, attr: dict):

    db = Database(db_path)

    db.create_table(attr, table_name)

    values = (1, 1, 'test', 'test', 'I', 'June 27, 2021')
    db.insert(values, table_name)

    values = (2, 2, 'test', 'test', 'I', 'June 27, 2021')
    db.insert(values, table_name)

    select = '*'
    results = db.select(select, 'profile')
    logger.debug(results)

    table_col = ('patient_num', 'last_name', 'middle_initial', 'dob')
    update_values = (4567, 'Tran', 'H', '06/27/2021')
    priority = 'last_name = "test"'
    db.update(update_values, table_name, table_col, priority)

    select = '*'
    results = db.select(select, table_name)
    logger.debug(results)

    priority = 'userID = 2'
    db.delete(table_name, priority)

    select = '*'
    results = db.select(select, table_name)
    logger.debug(results)

    db.close_connection()



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

    test_db(db_path, name, attr)
"""
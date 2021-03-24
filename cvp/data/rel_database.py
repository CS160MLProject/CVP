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
    """ Database instance for CRUD interaction """

    def __init__(self, db_path):
        """ construct the database

        Usage

        >>> from cvp.data.rel_database import Database
        >>> db = Database(db_path)

        Args:
             db_path (str): path to the database
        """
        Path(db_path).touch()

        self.conn = self.create_connection(db_path)
        self.engine = create_engine('sqlite:///' + db_path, echo=False)
        self.cursor = self.conn.cursor()

    def create_connection(self, db_path):
        """ Create a connection to database

        Args:
            db_path (str): path to database

        Returns:
             conn: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_path)
            logger.info('SUCCESS: Connected to Database')
            return conn
        except Error as e:
            logger.debug(e)

        return None

    def close_connection(self):
        """ Close the connection to database

        Usage:

        >>> from cvp.data.rel_database import Database
        >>> db = Database(db_path)
        >>> db.close_connection()

        Args:

        Returns:

        """
        if self.conn != None:
            self.conn.close()

        if self.engine != None:
            self.engine.dispose()

        logger.info('SUCCESS: Connection Closed')

    def create_table(self, attr: dict, table_name: str):
        """ Create new table

        Usage:

        >>> from cvp.data.rel_database import Database
        >>> db = Database(db_path)
        >>> db.create_table(attr, table_name)

        Args:
            attr (dict): column name and type
                Ex: attr = {'userID': 'INTEGER NOT NULL PRIMARY KEY'}
            table_name (str): name of table
        Returns:

        """
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
        """ Insert new values into existed table

        Usage:

        >>> from cvp.data.rel_database import Database
        >>> db = Database(db_path)
        >>> db.insert(values, table_name)

        Args:
            values (tuple): new values to insert
            talbe_name (str): name of table
        Returns:

        """
        SQL_Insert = f'''INSERT INTO {talbe_name} VALUES (?,?,?,?,?,?)'''
        try:
            self.cursor.execute(SQL_Insert, values)
            self.conn.commit()
            logger.info(f'SUCCESS: Insert into `{talbe_name}` successfully!')
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)

    def select(self, values: str, table_name: str, condition: str = None):
        """ Select values from existed table

        Usage:

        >>> from cvp.data.rel_database import Database
        >>> db = Database(db_path)
        >>> db.select(values, table_name, priority, condition=True)

        Args:
            values (str): columns to select from database
                Ex: values = 'userID, last_name, dob'
            condition (str): condition to select value
                Ex: condition = 'userID = 1 and last_name = "last"'
            table_name (str): name of table

        Returns:
            result (list): list of satisfied selection
        """
        SQL_Select = f'''SELECT {values} FROM {table_name}'''

        if condition:
            SQL_Select += f''' WHERE {condition}'''

        try:
            self.cursor.execute(SQL_Select)
            result = self.cursor.fetchall()
            logger.info('SUCCESS: Selection successfully!')

            return result
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)

    def update(self, values: tuple, table_cols: tuple, table_name: str, condition: str):
        """ Update values from existed table

        Usage:

        >>> from cvp.data.rel_database import Database
        >>> db = Database(db_path)
        >>> db.update(values, table_cols, table_name, condition)

        Args:
            table_cols (tuple): columns need to update
                Ex: table_cols = ('userID', 'last_name', 'dob')
            values (tuple): new values to update
                Ex: values = (1234, 'last', '12/31/2021')
            condition (str): condition to select value
                Ex: condition = 'userID = 1 and first_name = "first"'
            table_name (str): name of table

        Returns:

        """
        SQL_Update = f'''UPDATE {table_name} SET '''
        for col in table_cols:
            SQL_Update += f'''{col} = ?, '''
        SQL_Update = SQL_Update[:-2] + f''' WHERE {condition}'''

        logger.debug(SQL_Update)
        try:
            self.cursor.execute(SQL_Update, values)
            self.conn.commit()
            logger.info(f'SUCCESS: Update `{table_name}` successfully!')
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)

    def delete(self, table_name: str, condition: str):
        """ Detele values from existed table

        Usage:

        >>> from cvp.data.rel_database import Database
        >>> db = Database(db_path)
        >>> db.delete(table_name, condition)

        Args:
            table_name (str): name of table
            condition (str): condition to select values
                Ex: condition = 'userID = 1234'

        Returns:

        """
        SQL_Delete = f'''DELETE FROM {table_name} WHERE {condition}'''

        try:
            self.cursor.execute(SQL_Delete)
            self.conn.commit()
            logger.info(f'SUCCESS: Delete `{condition}` in `{table_name}` successfully!')
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
    db.update(update_values, table_col, table_name, priority)

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

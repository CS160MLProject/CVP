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
import coloredlogs

# Third party imports
from sqlite3 import Error
from pathlib import Path
from sqlalchemy import create_engine
from credentials import tuplex
import pandas as pd

# Project Level Imports

ACCOUNT_PATH = 'dataset/processed/accounts.txt'


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

    def create_table(self, attr: dict, table_name: str, foreign_key: dict = None):
        """ Create new table
        Usage:
        >>> from cvp.data.rel_database import Database
        >>> db = Database(db_path)
        >>> db.create_table(attr, table_name)
        Args:
            attr (dict): column name and type
                key = column_name, value = type of column
                Ex: attr = {'userID': 'INTEGER NOT NULL PRIMARY KEY'}
            foreign_key (dict): foreign key declaration
                key = column_name, value = table_name (table_name_col)
                Ex: foreign_key = {'user_account_id': 'profile (user_id)'}
            table_name (str): name of table
        Returns:
        """
        SQL_CreateTable = f'''CREATE TABLE IF NOT EXISTS {table_name} ('''
        for key, value in attr.items():
            SQL_CreateTable += f'''\n{key} {value},'''

        if foreign_key:
            for key, value in foreign_key.items():
                SQL_CreateTable += f'''\nFOREIGN KEY ({key}) REFERENCES {value},'''

        SQL_CreateTable = SQL_CreateTable[:-1] + '''\n)'''

        try:
            self.cursor.execute(SQL_CreateTable)
            logger.info(f'SUCCESS: Table `{table_name}` Created')
        except sqlite3.Error as e:
            logger.error(e)
            raise Exception(e)

    def insert(self, values: tuple, table_name: str):
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
        SQL_Insert = f'''INSERT INTO {table_name} VALUES (?'''

        for i in range(len(values)-1):
            SQL_Insert += ',?'
        SQL_Insert += ')'

        try:
            self.cursor.execute(SQL_Insert, values)
            self.conn.commit()
            logger.info(f'SUCCESS: Insert into `{table_name}` successfully!')
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
            result (list<tuple>): list of tuples with values
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


def main(db_path: dict, account_path: str = None):
    account_path = account_path or ACCOUNT_PATH
    if not os.path.exists(account_path):
        raise FileNotFoundError(f"File {account_path} was not found. Current dir: {os.getcwd()}")

    os.makedirs('dataset/external', exist_ok=True)

    # Make cvp.db
    logger.info('Preparing to make cvp database...')
    if os.path.exists(db_path.get('cvp')):
        os.remove(db_path.get('cvp'))

    if os.path.exists(db_path.get('cdc')):
        os.remove(db_path.get('cdc'))

    df = pd.read_csv(account_path, sep='\t')
    df.drop_duplicates(subset=['Email'], inplace=True)

    account_cols = ['Email', 'First_Name', 'Last_Name', 'Password', 'User_Account_ID', 'Salt']
    profile_cols = ['User_Account_ID', 'Patient_Num', 'Last_Name', 'First_Name', 'Middle_Initial', 'Dob',
                    'Vaccine_Name1', 'Vaccine_Date1', 'Hospital', 'Vaccine_Name2', 'Vaccine_Date2']

    db = Database(db_path.get('cvp'))

    account_df = df[account_cols].copy()
    account_df['Username'] = account_df['First_Name'] + " " + account_df['Last_Name']
    account_df.drop(['First_Name', 'Last_Name'], axis=1, inplace=True)

    table_name = 'profile'
    attr = {
        'User_Account_ID': 'INTEGER NOT NULL PRIMARY KEY',
        'Patient_Num': 'CHAR(4)',
        'Last_Name': 'VARCHAR NOT NULL',
        'First_Name': 'VARCHAR NOT NULL',
        'Middle_Initial': 'CHAR(1)',
        'Dob': 'VARCHAR NOT NULL',
        'Vaccine_Name1': 'VARCHAR NOT NULL',
        'Vaccine_Date1': 'VARCHAR NOT NULL',
        'Hospital': 'VARCHAR NOT NULL',
        'Vaccine_Name2': 'VARCHAR',
        'Vaccine_Date2': 'VARCHAR'
    }
    db.create_table(attr, table_name)
    df[profile_cols].to_sql(table_name, con=db.engine, if_exists='append', index=False)
    logger.info(f'SUCCESS: Insert values to `{table_name}` successfully!')

    logger.debug(f"Table `{table_name}`: {db.select('*', table_name)}")

    table_name = 'account'
    attr = {
        'Email': 'VARCHAR NOT NULL PRIMARY KEY',
        'Password': 'VARCHAR NOT NULL',
        'User_Account_ID': 'INTEGER NOT NULL',
        'Salt': 'VARCHAR NOT NULL',
        'Username': 'VARCHAR NOT NULL'
    }
    foreign_key = {
        'User_Account_ID': 'profile (User_Account_ID)'
    }
    db.create_table(attr, table_name, foreign_key)
    account_df.to_sql(table_name, con=db.engine, if_exists='append', index=False)
    logger.info(f'SUCCESS: Insert values to `{table_name}` successfully!')

    logger.debug(f"Table `{table_name}`: {db.select('*', table_name)}")

    db.close_connection()

    # Make cdc.db
    logger.info('Preparing to make cdc database...')
    table_name = 'profile'
    attr = {
        'Email': 'VARCHAR NOT NULL PRIMARY KEY',
        'Patient_Num': 'INTEGER',
        'Last_Name': 'VARCHAR NOT NULL',
        'First_Name': 'VARCHAR NOT NULL',
        'Middle_Initial': 'CHAR(1)',
        'Dob': 'VARCHAR NOT NULL',
        'Vaccine_Name1': 'VARCHAR NOT NULL',
        'Vaccine_Date1': 'VARCHAR NOT NULL',
        'Hospital': 'VARCHAR NOT NULL',
        'Vaccine_Name2': 'VARCHAR',
        'Vaccine_Date2': 'VARCHAR'
    }
    profile_cols = ['Email', 'Patient_Num', 'Last_Name', 'First_Name', 'Middle_Initial', 'Dob',
                    'Vaccine_Name1', 'Vaccine_Date1', 'Hospital', 'Vaccine_Name2', 'Vaccine_Date2']

    db = Database(db_path.get('cdc'))
    db.create_table(attr, table_name)
    df[profile_cols].to_sql(table_name, con=db.engine, if_exists='append', index=False)
    logger.info(f'SUCCESS: Insert values to `{table_name}` successfully!')

    for element in tuplex:
        db.insert(element, table_name)

    logger.debug(f"Table `{table_name}`: {db.select('*', table_name)}")

    db.close_connection()

    logger.info('Finished operation')


if __name__ == "__main__":
    db_path = {
        'cvp': 'dataset/external/cvp.db',
        'cdc': 'dataset/external/cdc.db'
    }
    main(db_path)
from flask import Flask
from flask_mail import Mail
from cvp.data.rel_database import Database

app = Flask(__name__, template_folder='cvp/app/templates')  # , instance_relative_config=True)
mail = Mail(app)

# db operation
db_path = 'cvp/data'
db = Database(db_path)
db.create_connection(db_path)

db.create_table(attr={'account_id': 'INTEGER NOT NULL PRIMARY KEY', 'email': 'VARCHAR NOT NULL',
                      'password': 'VARCHAR NOT NULL', 'salt': 'VARCHAR NOT NULL',
                      'first_name': 'VARCHAR NOT NULL', 'last_name': 'VARCHAR NOT NULL'},
                table_name='account')

db.create_table(attr={'user_id': 'INTEGER NOT NULL PRIMARY KEY', 'patient_num': 'VARCHAR NOT NULL',
                      'first_name': 'VARCHAR NOT NULL', 'last_name': 'VARCHAR NOT NULL', 'mid_i': 'CHAR(1)',
                      'Dob': 'DATE NOT NULL', 'vaccine_name': 'VARCHAR NOT NULL',
                      'hospital': 'VARCHAR NOT NULL', 'first_date': 'DATE NOT NULL',
                      'second_date': 'DATE NOT NULL'}, table_name='profile')

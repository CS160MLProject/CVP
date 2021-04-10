from flask import Flask
from flask_mail import Mail
from cvp.data.rel_database import Database
from cvp.model.ocr_model import OCR_Model

app = Flask(__name__, template_folder='cvp/app/templates')  # , instance_relative_config=True)
mail = Mail(app)
model = OCR_Model()

# db operation
db_path = 'dataset/external/cvp.db'
db = Database(db_path)
db.create_connection(db_path)
#
# account_attrs = {
#         'Account_ID': 'INTEGER NOT NULL PRIMARY KEY',
#         'Email': 'VARCHAR NOT NULL',
#         'Password': 'BLOB NOT NULL',
#         'Salt': 'VARCHAR NOT NULL',
#         'Last_Name': 'VARCHAR NOT NULL',
#         'First_Name': 'VARCHAR NOT NULL'
#     }
# foreign_key = {
#     'User_Account_ID': 'account (User_Account_ID)'
# }
# profile_attrs = {
#         'User_Account_ID': 'INTEGER NOT NULL PRIMARY KEY',
#         'Patient_Num': 'INTEGER NOT NULL',
#         'Last_Name': 'VARCHAR NOT NULL',
#         'First_Name': 'VARCHAR NOT NULL',
#         'Middle_Initial': 'CHAR(1)',
#         'Dob': 'VARCHAR NOT NULL',
#         'Hospital': 'VARCHAR NOT NULL',
#         'Vaccine_Name': 'VARCHAR NOT NULL',
#         'Date1': 'VARCHAR NOT NULL',
#         'Date2': 'VARCHAR NOT NULL'
#     }
# db.create_table(attr=account_attrs, table_name='account')
# db.create_table(attr=profile_attrs, table_name='profile', foreign_key=foreign_key)

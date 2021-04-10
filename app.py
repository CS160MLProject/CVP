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

account_table = 'accounts'
profile_table = 'profile'


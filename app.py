from flask import Flask
from flask_mail import Mail
from cvp.model.ocr_model import OCR_Model
from credentials import *


# app = None
# mail = None
# model = None

# db operation
db_path = 'dataset/external/cvp.db'
account_table = 'account'
profile_table = 'profile'


def create_app():
    app = Flask(__name__, template_folder='cvp/app/templates')
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    return app


def set_mail():
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = support_email
    app.config['MAIL_PASSWORD'] = support_email_pass


app = create_app()
model = OCR_Model()
set_mail()
mail = Mail(app)




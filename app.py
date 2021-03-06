from flask import Flask
from flask_mail import Mail
from cvp.model.ocr_model import OCR_Model
from dotenv import load_dotenv
import os

load_dotenv()

# db operation
db_path = 'dataset/external/cvp.db'
cdc_db_path = 'dataset/external/cdc.db'
account_table = 'account'
profile_table = 'profile'

# AWS S3 bucket
bucket_name = 'covapass-photo'
profile_bucket = 'profile_photo/'


def create_app():
    app = Flask(__name__, template_folder='cvp/app/templates')
    app.config['DEBUG'] = True
    app.config['TESTING'] = False
    app.secret_key = os.environ['secret_key']
    return app


def set_mail():
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.environ['support_email']
    app.config['MAIL_PASSWORD'] = os.environ['support_email_pass']


app = create_app()
model = OCR_Model()
set_mail()
mail = Mail(app)


if __name__ == '__main__':
    from cvp.app.routes import *
    app.run(debug=True, port=5000, host='0.0.0.0')


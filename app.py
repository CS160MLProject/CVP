from flask import Flask
from flask_mail import Mail
from cvp.model.ocr_model import OCR_Model
from credentials import *


def create_app():
    cvp_app = Flask(__name__, template_folder='cvp/app/templates')
    cvp_app.config['DEBUG'] = True
    cvp_app.config['TESTING'] = True
    return cvp_app


app = create_app()
model = OCR_Model()

# mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = support_email
app.config['MAIL_PASSWORD'] = support_email_pass
mail = Mail(app)


# db operation
db_path = 'dataset/external/cvp.db'
account_table = 'account'
profile_table = 'profile'


if __name__ == '__main__':
    app.run(debug=True)
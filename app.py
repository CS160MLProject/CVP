from flask import Flask
from flask_mail import Mail


app = Flask(__name__, template_folder='cvp/app/templates')
mail = Mail(app)

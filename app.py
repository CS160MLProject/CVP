from flask import Flask
from flask_mail import Mail


app = Flask(__name__, template_folder='cvp/app/templates', instance_relative_config=True)
mail = Mail(app)

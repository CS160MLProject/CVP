from flask import Flask
from flask_mail import Mail


app = Flask(__name__, template_folder='cvp/app/templates')#, instance_relative_config=True)
mail = Mail(app)

## keys to be changed and removed when deploying
profile_key = 'profile_key'
recovery_key = 'recovery_key'
change_account_key = 'change_account_profile_key'
sharing_profile_key = 'sharing_key'
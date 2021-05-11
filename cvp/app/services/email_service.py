from flask_mail import Message
from flask import render_template
from app import *
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

def __send_password_recovery_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_password_recovery_email(url, recipient):
    msg = Message()
    msg.subject = 'Password Reset Requested'
    msg.recipients = [recipient]
    msg.sender = os.environ['support_email']
    msg.html = render_template("email/password_recovery.html", recover_url=url)
    Thread(target=__send_password_recovery_email, args=(app, msg)).start()

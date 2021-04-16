from flask_mail import Message
from app import *

from threading import Thread


def __send_password_recovery_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_password_recovery_email(html, recipient):
    msg = Message()
    msg.subject = 'Password Reset Requested'
    msg.recipients = [recipient]
    msg.sender = support_email
    msg.body = f'{msg.subject}, {html}'
    Thread(target=__send_password_recovery_email, args=(app, msg)).start()

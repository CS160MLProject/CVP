from flask_mail import Message
from app import *

from threading import Thread


def __send_password_recovery_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, html, recipient):
    msg = Message()
    msg.subject = subject
    msg.recipients = [recipient]
    msg.sender = support_email
    msg.body = f'{subject}, {html}'
    Thread(target=__send_password_recovery_email, args=(app, msg)).start()

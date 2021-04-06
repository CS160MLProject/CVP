from flask_mail import Message
from threading import Thread

from app import app
from app import mail


# def send_async_email(app, msg):
#     with app.app_context():
#         try:
#             mail.send(msg)
#         except ConnectionRefusedError:
#             raise InternalServerError("[MAIL SERVER] not working")


def send_email(email, subject, html):
    # msg = Message(subject, sender=sender, recipients=recipients)
    # msg.body = text_body
    # msg.html = html_body
    # Thread(target=send_async_email, args=(app, msg)).start()
    print(email, subject, html)

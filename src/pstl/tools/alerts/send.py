import smtplib
from email.message import EmailMessage
import requests

def send(to,subject, body, Sender):
    """
    Sender is a class with subclasses EMAIL and API
    attributes=example
    Sender.Email.address='sample@gmail.com'
    Sendr.Email.password='third-party app password'
    Sender.Email.smtp='smtp.gmail.com'
    Sender.Email.port=587
    """

    msg=EmailMessage()
    msg.set_content(body)
    msg['subject']=subject
    msg['to']=to

    msg['from']=Sender.Email.address
    password=Sender.Email.password
    server = smtplib.SMTP(Sender.Email.smtp,Sender.Email.port)

    server.starttls()
    server.login(Sender.Email.address, Sender.Email.password)
    server.send_message(msg)

    server.quit()

def text(to,subject, body, Sender):
    send(to,subject,body,Sender)

def email(to,subject, body, Sender):
    send(to,subject,body,Sender)

def api(to,subject,body,Sender):
    """
    Sender is a class with subclasses EMAIL and API
    attributes=example
    Sender.Api.app='https://api.mynotifier.app'
    Sender.Api.msgtype="info"

    """
    requests.post(Sender.Api.app, {
        "apiKey": to,
        "message": subject,
        "description": body,
        "type": Sender.Api.msgtype, # info, error, warning or success
        })


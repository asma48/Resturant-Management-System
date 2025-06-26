import smtplib
from smtplib import SMTPException
import random 


def send_OTP_email(to_email:str):   
    otp = ""
    for i in range(4):
        otp += str(random.randint(0,9))

    sender = "no-reply@yourapp.com"
    receiver = to_email

    message = f"""\
Subject: OTP Verification
To: {receiver}
From: {sender}

Your OTP code is: {otp}"""
    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login("a4b9050ae8525c", "15fedc88bde636")
            server.sendmail(sender, receiver, message)
    except SMTPException as e:
        print("Failed to send OTP:", e)
    return otp
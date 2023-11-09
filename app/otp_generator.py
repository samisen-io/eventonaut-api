import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
port = int(os.getenv("EMAIL_PORT"))
server = os.getenv("EMAIL_SERVER")

default_time_limit = int(os.getenv("OTP_EXPIRE"))

def generate_otp():
    otp = ''.join(random.choice(string.digits) for _ in range(6))
    return otp

def validate_otp(gen_otp:str, rec_otp: str, gen_time:datetime, rec_time:datetime):
    if gen_otp == rec_otp and (rec_time - gen_time).total_seconds() <= default_time_limit:
        return True
    return False

def send_mail(otp: str,subject: str, receiver_email:str):
    try:
        global default_time_limit, email, password, port, server
        smtp_port = port
        smtp_server = server
        sender_email = email
        password = password

        body = f""" 
        Hello user,<br>
            Your <b>One Time Password</b> is - <b>{otp}</b>, and is valid for only <b>{default_time_limit // 60} minutes</b>
        """

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        print("Connecting to server...")
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
        except Exception as e:
            print(e)
            print("Error: unable to connect to server")
            return False
        try:
            server.starttls()
        except Exception as e:
            print(e)
            print("Error: unable to start tls")
            return False
        try:
            server.login(sender_email, password)
        except Exception as e:
            print(e)
            print("Error: unable to login")
            return False
        print("Connected to server")

        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print("Email sent successfully")

        server.quit()
        return True
    except Exception as e:
        print(e)
        print("Error: unable to send email")
        return False
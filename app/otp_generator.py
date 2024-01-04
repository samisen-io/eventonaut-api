import random
import logging
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

default_time_limit = int(os.getenv("OTP_EXPIRE"))

def generate_otp():
    otp = ''.join(random.choice(string.digits) for _ in range(6))
    return otp

def validate_otp(gen_otp:str, rec_otp: str):
    if gen_otp == rec_otp:
        return True
    return False

def send_mail(otp: str,subject: str, receiver_email:str):
    try:
        global default_time_limit, email, password, port, server
        smtp_port = 587
        smtp_server = "smtp.gmail.com"
        sender_email = email
        password = password

        if not smtp_server or not smtp_port:
            print("Error: smtp server or port not found")
            return False
        
        if not sender_email or not password:
            print("Error: sender email or password not found")
            return False

        body = f""" 
        Hello user,<br>
            Your <b>One Time Password</b> is - <b>{otp}</b>, and is valid for only <b>{default_time_limit // 60} minutes</b>
        """

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        logging.info("Connecting to server")
        server = smtplib.SMTP(smtp_server, smtp_port)

        server.starttls()

        server.login(sender_email, password)
        logging.info("Login successful")

        text = msg.as_string()
        
        server.sendmail(sender_email, receiver_email, text)
        logging.info("Email sent successfully")
        
        return True
    except Exception as e:
        logging.exception(str(e))
        return False
    
    finally:
        try:
            server.quit()
            logging.info("Server closed")
        except Exception as e:
            logging.exception(str(e))
            return False
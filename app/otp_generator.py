from email.mime.application import MIMEApplication
import random
import logging
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from .email_templates.welcome_user import WelcomeUserEnum
from .routers.upload_image import download_ticket

load_dotenv()

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
command_center_link = os.getenv("COMMAND_CENTER_PATH")

default_time_limit = int(os.getenv("OTP_EXPIRE"))

def generate_otp():
    otp = ''.join(random.choice(string.digits) for _ in range(6))
    return otp

def validate_otp(gen_otp:str, rec_otp: str):
    if gen_otp == rec_otp:
        return True
    return False

def send_mail(unique_id: str, subject: str, receiver_email:str, first_name:str, email_template: WelcomeUserEnum):
    try:
        global email, password, command_center_link
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

        body = email_template.email(first_name=first_name, command_center_link=command_center_link, receiver_email=receiver_email, unique_id=unique_id)

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
        
def send_tickets(receiver_email: str, blob_url: str, subject: str):
    try:
        global email, password, command_center_link
        smtp_port = 587
        smtp_server = "smtp.gmail.com"
        sender_email = email
        password = password
        
        ticket = download_ticket(blob_url)
        
        logging.info("Connecting to server")
        server = smtplib.SMTP(smtp_server, smtp_port)

        server.starttls()

        server.login(sender_email, password)
        logging.info("Login successful")

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Message body
        body = "Please find attached your tickets."
        msg.attach(MIMEText(body, 'plain'))

        # PDF attachment from memory
        part = MIMEApplication(ticket, Name="Ticket.pdf")
        part['Content-Disposition'] = 'attachment; filename="Ticket.pdf"'
        msg.attach(part)

        server.send_message(msg)
        logging.info(f"Email sent to {receiver_email}")

    except Exception as e:
        logging.exception(f"failing to send email to {receiver_email} due to {str(e)}")
        return False
    finally:
        server.quit()
        logging.info("Server closed")

    return True
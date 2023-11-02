import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class otp_generator:

    __otp: int = None
    __gen_time: datetime = None
    default_time_limit: int = 300

    def generate_otp(self):
        self.__otp = int(''.join(random.choice(string.digits) for i in range(6)))
        self.__gen_time = datetime.now()
        return self.__otp

    def validate_otp(self, otp:int, validaton_time:datetime):
        if self.__otp == otp and (validaton_time - self.__gen_time).seconds <= self.default_time_limit:
            valid = True
            self.__otp = None
            self.__gen_time = None
        else:
            valid = False
        return valid        

def send_mail(otp: otp_generator,subject: str, receiver_email:str):
    smtp_port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "demo34125@gmail.com"
    password = "orse wxwr crjv sxry"

    body = f""" 
    Hello user,<br>
        Your <b>One Time Password</b> is - <b>{otp.generate_otp()}</b>, and is valid for only <b>{otp.default_time_limit // 60} minutes</b>
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    print("Connecting to server...")
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, password)
    print("Connected to server")

    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    print("Email sent successfully")

    server.quit()

if __name__ == "__main__":
    otp = otp_generator()
    send_mail(otp, "OTP Verification","demo34125@gmail.com")
    one_tme_pass = int(input("Enter otp: "))
    validation_time = datetime.now()
    print("My Otp is: ", one_tme_pass)
    print("actual otp is: ", otp._otp)  
    print(otp.validate_otp(one_tme_pass, validation_time))
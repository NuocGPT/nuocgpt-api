import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.config import Settings


smtp_host = Settings().SMTP_HOST
smtp_port = Settings().SMTP_PORT
smtp_user = Settings().SMTP_USER
smtp_pass = Settings().SMTP_PASS
context = ssl.create_default_context()

def send_mail(subject: str, receiver_email: str, content: MIMEText):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = smtp_user
    message["To"] = receiver_email
    message.attach(content)
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(
            smtp_user, receiver_email, message.as_string()
        )


def get_otp_message(otp: str):
    html = """\
        <html>
            <body>
                <p>Hello, the verification code is: <strong>{}</strong></p>
            </body>
        </html>
        """
    return MIMEText(html.format(otp), "html")


def send_otp(email: str, verify_code: int):
    message = get_otp_message(verify_code)
    send_mail("OTP verification", email, message)
    return True


def send_otp_forgot_password(email: str, verify_code: int):
    message = get_otp_message(verify_code)
    send_mail("Forgot Password", email, message)
    return True

from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
from app.config import settings  # Ensure this loads SMTP config

def send_email(subject: str, recipient: str, body: str, subtype: str = "plain"):
    smtp_email = settings.SMTP_EMAIL
    smtp_password = settings.SMTP_PASSWORD
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT

    if not smtp_email or not smtp_password:
        raise ValueError("Thiếu SMTP_EMAIL hoặc SMTP_PASSWORD trong file .env")

    # Tạo email message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = smtp_email
    msg["To"] = recipient

    # Thêm phần nội dung email với định dạng plain hoặc html
    msg.attach(MIMEText(body, subtype, "utf-8"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError("Lỗi xác thực SMTP: Kiểm tra lại SMTP_EMAIL hoặc SMTP_PASSWORD")
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Lỗi khi gửi email: {e}")

import smtplib
from email.message import EmailMessage
import os

from app.config import settings

EMAIL_FROM = settings.SMTP_EMAIL
EMAIL_PASSWORD = settings.SMTP_PASSWORD
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")  # mặc định React ở 3000

def get_smtp_config():
    return {
        "host": "smtp.gmail.com",  # Vì bạn dùng Gmail
        "port": 587,
        "use_tls": True
    }

def generate_random_password(length=8):
    import string, random
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def send_new_password_email(email: str, new_password: str):
    subject = "🔑 Mật khẩu mới của bạn | VLU Chatbot"

    body = f"""
    <html>
      <body>
        <p>Xin chào,</p>

        <p>Bạn vừa yêu cầu <strong>đặt lại mật khẩu</strong> cho tài khoản Chatbot của mình.</p>

        <p>Mật khẩu mới của bạn là:</p>
        <h2 style="color:#007bff;"> {new_password}</h2>

        <p> Vui lòng sử dụng mật khẩu này để đăng nhập, và <strong>đổi lại mật khẩu ngay sau đó</strong> để bảo mật tài khoản.</p>

        <p>Trân trọng,<br/>VLU Chatbot</p>
      </body>
    </html>
    """

    send_email(subject=subject, recipient=email, body=body, subtype="html")

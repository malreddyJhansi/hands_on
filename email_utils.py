import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def build_email(sender, recipient, subject, body, attachment_path=None):
    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = sender, recipient, subject
    msg.attach(MIMEText(body, "plain"))
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            mime_base = MIMEBase("application", "octet-stream")
            mime_base.set_payload(f.read())
            encoders.encode_base64(mime_base)
            mime_base.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attachment_path)}"')
            msg.attach(mime_base)
    return msg

def send_email(msg, smtp_server, smtp_port, username, password):
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")


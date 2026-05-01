import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()


# SMTP server configuration
smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
smtp_port = int(os.getenv("SMTP_PORT", "587"))
sender_email = os.getenv("SMTP_SENDER_EMAIL", "")
app_password = os.getenv("SMTP_APP_PASSWORD", "")
print("EMAIL:", sender_email)
print("PASSWORD:", app_password)

def send_email(recipient_email: str, subject: str, message: str):
    if not sender_email or not app_password:
        raise RuntimeError("SMTP credentials are not configured in environment variables.")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")
        
# if __name__ == "__main__":
#     send_email("vinaypate94@gmail.com", "Test Email", "Hello, this is a test")
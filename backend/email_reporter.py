import smtplib
from email.message import EmailMessage
import os

def send_report(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = os.environ["EMAIL_TO"]
    msg.set_content(body)

    server = os.environ["EMAIL_HOST"]
    port = int(os.environ["EMAIL_PORT"])
    user = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]

    print(f"Connecting to SMTP server {server} on port {port}...")
    try:
        with smtplib.SMTP(server, port, timeout=30) as smtp:
            print("Connection successful. Starting TLS...")
            smtp.starttls()
            print("TLS started. Logging in...")
            smtp.login(user, password)
            print("Login successful. Sending message...")
            smtp.send_message(msg)
            print("Message sent.")
    except Exception as e:
        print(f"EMAIL_ERROR: An exception occurred while sending email: {e}")
        # Re-raise the exception so the main script can handle it
        raise 
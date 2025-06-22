import smtplib
import os
from email.message import EmailMessage

def send_report(subject, body):
    """
    Sends an email report using credentials stored in environment variables.
    """
    try:
        smtp_server = os.environ["EMAIL_HOST"]
        smtp_port = int(os.environ["EMAIL_PORT"])
        smtp_user = os.environ["EMAIL_USER"]
        smtp_pass = os.environ["EMAIL_PASS"]
        email_to = os.environ["EMAIL_TO"]
        email_cc = os.getenv("EMAIL_CC") # Use os.getenv for optional CC

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"VortexSync Automation <{smtp_user}>"
        msg["To"] = email_to
        if email_cc:
            msg["Cc"] = email_cc
        msg.set_content(body)

        print("Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            print("Logging in...")
            smtp.login(smtp_user, smtp_pass)
            print("Sending message...")
            smtp.send_message(msg)
            print("Email report sent successfully.")

    except KeyError as e:
        print(f"ERROR: Email secret not found: {e}. Please set all email environment variables.")
    except Exception as e:
        print(f"ERROR: Failed to send email report: {e}") 
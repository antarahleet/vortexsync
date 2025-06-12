# 🛫 Deploying VortexSync to Fly.io (Python + Playwright)

This document contains step-by-step deployment instructions for the VortexSync backend, which runs Playwright to automate lead migration from Vortex to Boldtrail. Your goal is to set this up as a daily scheduled cloud-based task using Fly.io.

⚠️ After each step, **STOP and wait** for the user to confirm before continuing.

---

## STEP 1 — SETUP FILE STRUCTURE

1. Make sure the project root contains the following structure:

```
vortexsync/
│
├── backend/
│   ├── playwright/
│   │   ├── expired_scraper.py
│   │   ├── utils.py
│   │   └── ...
│   └── email_reporter.py       # (we'll create this later)
│
├── requirements.txt            # include all necessary packages
├── Dockerfile                  # (you will create this next)
├── fly.toml                    # (will be generated)
└── .env                        # for local use only, not used in production
```

✅ Ask the user to confirm the file tree is accurate before continuing.

---

## STEP 2 — CREATE DOCKERFILE

1. In the project root, create a file named `Dockerfile` and paste the following content:

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.41.1

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "backend/playwright/expired_scraper.py"]
```

2. Save the file.

✅ STOP and ask the user to confirm the Dockerfile was created and saved properly.

---

## STEP 3 — INSTALL FLY.IO CLI & INIT APP

1. Ask the user to open a terminal and run the following to install the Fly.io CLI:

```bash
curl -L https://fly.io/install.sh | sh
```

2. Then log in:

```bash
fly auth login
```

3. Next, initialize the app (do not deploy yet):

```bash
fly launch --name vortexsync --no-deploy
```

✅ WAIT for the user to confirm Fly is installed and the `fly.toml` file was created.

---

## STEP 4 — ADD ENVIRONMENT SECRETS TO FLY

Ask the user for the following values (if not already provided):

- VORTEX_USERNAME
- VORTEX_PASSWORD
- BOLDTRAIL_USERNAME
- BOLDTRAIL_PASSWORD
- EMAIL_TO
- SMTP_SERVER
- SMTP_USER
- SMTP_PASS

Then instruct the user to run:

```bash
fly secrets set VORTEX_USERNAME="..." VORTEX_PASSWORD="..." BOLDTRAIL_USERNAME="..." BOLDTRAIL_PASSWORD="..." EMAIL_TO="..." SMTP_SERVER="..." SMTP_USER="..." SMTP_PASS="..."
```

✅ STOP and confirm all secrets were set before continuing.

---

## STEP 5 — CREATE THE EMAIL REPORT MODULE

1. In `backend/email_reporter.py`, create a new Python file with this content:

```python
import smtplib
from email.message import EmailMessage
import os

def send_report(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["EMAIL_TO"]
    msg.set_content(body)

    with smtplib.SMTP_SSL(os.environ["SMTP_SERVER"], 465) as smtp:
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        smtp.send_message(msg)
```

✅ STOP and verify this file exists and is saved correctly.

---

## STEP 6 — UPDATE `expired_scraper.py` TO USE EMAIL REPORTING

1. At the end of `expired_scraper.py`, import and call `send_report()`:

```python
from backend.email_reporter import send_report

send_report(
    subject="VortexSync - 3 leads were migrated to Boldtrail",
    body="Migration completed successfully with 3 leads uploaded."
)
```

✅ WAIT for the user to confirm the script ends with the `send_report()` call.

---

## STEP 7 — DEPLOY TO FLY.IO

1. Run this in the terminal to deploy the app:

```bash
fly deploy
```

2. Wait for deployment to finish.

✅ STOP and ask the user to confirm deployment was successful.

---

## STEP 8 — SCHEDULE DAILY CRON JOB

Now set up a daily cron job that runs the script at 9AM UTC every day:

```bash
fly cron schedule   "daily-expireds"   "0 9 * * *"   --command "python backend/playwright/expired_scraper.py"
```

✅ Confirm with the user that the cron job was added.

---

## ✅ DONE!

Once this is complete, your backend is fully deployed, and VortexSync will automatically run daily and email you the results.

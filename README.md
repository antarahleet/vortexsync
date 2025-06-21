# VortexSync: Automated Real Estate Lead Migration

VortexSync is a lightweight, automated tool that scrapes "Expired" real estate listings from the Vortex platform and migrates them as new leads into the BoldTrail CRM.

The entire process is orchestrated by a GitHub Actions workflow that runs on a daily schedule, ensuring a fresh list of leads is in your CRM every morning without any manual intervention.

## How It Works

1.  **Scheduled Trigger**: A GitHub Actions workflow (`.github/workflows/daily_migration.yml`) runs at 8:30 AM ET every day. It can also be triggered manually.
2.  **Environment Setup**: The workflow sets up a fresh environment, installs Python dependencies, and installs the Playwright browser automation tool.
3.  **Scraping**: The main script (`expired_scraper.py`) securely logs into Vortex using credentials stored in GitHub Secrets.
4.  **Data Extraction**: It navigates to the "Expireds" section, scrapes the relevant lead data, and logs out.
5.  **Data Migration**: The script then logs into BoldTrail, navigates to the manual lead creation page, and enters the scraped data, using utility functions from `boldtrail_utils.py`.
6.  **Reporting**: Upon completion (or failure), the script uses `email_reporter.py` to send a detailed status report to a designated email address.

## File Structure

Here is a breakdown of the key files in this project:

```
VortexSync/
├── .github/workflows/daily_migration.yml   # The core GitHub Actions workflow
├── .env.example                            # Example file for local environment variables
├── boldtrail_utils.py                      # Functions for interacting with BoldTrail
├── email_reporter.py                       # Handles sending success/failure email reports
├── expired_scraper.py                      # The main scraper and migration script
└── requirements.txt                        # Python dependencies
```

## Setup and Configuration for Your Use

To get this running on your own fork of the repository, you need to configure your account credentials and email settings. This is done by adding **Secrets** to your GitHub repository.

### Step 1: Create a `.env` file for local testing (Optional)

For running the script on your local machine, you can create a `.env` file in the root of the project. This file is ignored by Git and keeps your credentials private.

Create a file named `.env` and copy the contents of `.env.example`, then fill in your details.

```ini
# Vortex Credentials
VORTEX_USER="your-vortex-email@example.com"
VORTEX_PASS="your-vortex-password"

# BoldTrail Credentials
BOLDTRAIL_USER="your-boldtrail-email@example.com"
BOLDTRAIL_PASS="your-boldtrail-password"

# Email Reporting Settings
EMAIL_TO="recipient@example.com"
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_USER="your-sending-email@gmail.com"
EMAIL_PASS="your-gmail-app-password"
```
> **Important**: For `EMAIL_PASS` with a Gmail account, you must use a 16-character **App Password**, not your regular login password. [Learn how to create one here.](https://support.google.com/accounts/answer/185833)

### Step 2: Set up GitHub Secrets for Automation

The automated workflow relies on GitHub Secrets to access your credentials securely. You must set these in your forked repository.

1.  In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**.
2.  Click the **New repository secret** button for each secret below.
3.  The "Name" of the secret must match the variable names exactly. The "Value" should be your personal credential.

#### Required Secrets:

| Secret Name        | Description                                     | Example Value                    |
| ------------------ | ----------------------------------------------- | -------------------------------- |
| `VORTEX_USER`      | Your login email for the Vortex platform.       | `agent@example.com`              |
| `VORTEX_PASS`      | Your login password for the Vortex platform.    | `VortexPassword123`              |
| `BOLDTRAIL_USER`   | Your login email for the BoldTrail CRM.         | `agent@boldtrail.com`            |
| `BOLDTRAIL_PASS`   | Your login password for the BoldTrail CRM.      | `BoldtrailPassword456`           |
| `EMAIL_TO`         | The email address to send reports to.           | `your-personal-email@outlook.com` |
| `EMAIL_HOST`       | The SMTP server for your email provider.        | `smtp.gmail.com`                 |
| `EMAIL_PORT`       | The SMTP port (usually 587 for TLS).            | `587`                            |
| `EMAIL_USER`       | The username for your sending email account.    | `your-automation-email@gmail.com`|
| `EMAIL_PASS`       | The password or App Password for the email.     | `abdcivogzxjhyqwt`               |

## Running the Workflow

The workflow is scheduled to run automatically. If you want to run it manually:

1.  Go to the **Actions** tab in your GitHub repository.
2.  Click on the **Daily Expireds Migration** workflow in the left sidebar.
3.  Click the **Run workflow** dropdown, select the `main` branch, and click the **Run workflow** button.

You can monitor the progress in the Actions tab and will receive an email report once it's complete.
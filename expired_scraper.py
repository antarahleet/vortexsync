import os
import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import pathlib
from boldtrail_utils import transform_vortex_to_boldtrail_csv, upload_csv_to_boldtrail

VORTEX_LOGIN_URL = "https://vortex.theredx.com/login"
DOWNLOAD_DIR = pathlib.Path(__file__).resolve().parent / "cache" / "downloads"
SOURCE_NAME = "Daily Expireds" # Define the source for logging and notes

def run_expired_migration():
    """
    Orchestrates the migration of 'Daily Expireds' from Vortex to Boldtrail.
    Yields log messages as it progresses.
    """
    playwright = None
    browser = None
    context = None
    page = None
    # Check if running in the Fly.io environment
    is_production = 'FLY_APP_NAME' in os.environ
    
    # Launch Playwright
    try:
        yield "Starting migration for: Daily Expireds"
        load_dotenv()
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        playwright = sync_playwright().start()
        
        # Launch non-headless for local debugging if HEADLESS=false is set.
        # Defaults to headless for production/unspecified environments.
        headless_mode = os.getenv("HEADLESS", "true").lower() == "true"
        yield f"Launching browser in {'headless' if headless_mode else 'headed'} mode."
        browser = playwright.chromium.launch(headless=headless_mode)
        
        # Use a non-incognito context to better mimic real user behavior
        # Set a large viewport for headless mode to ensure all desktop UI elements are visible.
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        # --- Part 1: Download from Vortex ---
        yield "Navigating to Vortex login page..."
        page.goto(VORTEX_LOGIN_URL, timeout=60000)
        page.wait_for_timeout(500)
        
        yield "Entering credentials and logging in..."
        page.wait_for_timeout(1000) 
        page.keyboard.press("Tab")
        page.keyboard.type(os.getenv("VORTEX_USER"))
        page.keyboard.press("Tab")
        page.keyboard.type(os.getenv("VORTEX_PASS"))
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)

        yield "Waiting for dashboard to load..."
        page.wait_for_selector("text=Welcome", timeout=60000)
        page.wait_for_timeout(500)
        yield "Dashboard loaded successfully."
        
        # Handle the new onboarding modal if it appears
        yield "Checking for onboarding modal..."
        try:
            setup_later_button = page.locator("button:has-text('Set Up Later')")
            if setup_later_button.is_visible(timeout=5000):
                setup_later_button.click()
                yield "Clicked 'Set Up Later' to dismiss onboarding modal."
                page.wait_for_timeout(1000)
        except:
            yield "No onboarding modal found, proceeding..."
        
        # Navigate to Prospects section
        yield "Navigating to Prospects section..."
        prospects_link = page.locator("a.top-navbar__app-link:nth-child(1)")
        prospects_link.wait_for(state="visible", timeout=90000)
        prospects_link.click()
        page.wait_for_timeout(2000)
        yield "Clicked on Prospects section."
        page.wait_for_timeout(500)

        yield f"Searching for expired leads in the new interface..."
        
        # Look for the "Expired" section in the New Leads widget
        try:
            # First try to find the "Expired" text in the New Leads section
            expired_section = page.locator("text=Expired")
            expired_section.wait_for(state="visible", timeout=30000)
            expired_section.click()
            yield "Clicked on 'Expired' section in New Leads."
            page.wait_for_timeout(2000)
        except:
            # Fallback: try to find any element containing "Expired" and click it
            yield "Trying alternative method to find expired leads..."
            expired_elements = page.locator("*:has-text('Expired')")
            if expired_elements.count() > 0:
                expired_elements.first.click()
                yield "Clicked on first 'Expired' element found."
                page.wait_for_timeout(2000)
            else:
                raise Exception("Could not find 'Expired' section in the new Vortex interface")
        
        yield "Waiting for lead data to load..."

        yield "Waiting for and clicking 'Select All' checkbox..."
        select_all_checkbox = page.locator("#vxtb-button-check")
        select_all_checkbox.wait_for(state="visible", timeout=90000)
        page.wait_for_timeout(500)
        select_all_checkbox.click()
        page.wait_for_timeout(500)
        yield "Clicked 'Select All'."
        page.wait_for_timeout(1000)

        yield "Waiting for and clicking 'More' button..."
        more_button = page.locator('div.top-navbar__more-button:has-text("More")')
        more_button.wait_for(state="visible", timeout=90000)
        page.wait_for_timeout(500)
        
        yield "Checking for and removing potential popups..."
        # Remove the Intercom chat widget if it exists
        page.evaluate("document.querySelector('#intercom-container')?.remove()")
        # Remove the new Admin Custom Popup if it exists
        page.evaluate("document.querySelector('admin-custom-popup')?.remove()")
        page.wait_for_timeout(250) # Brief pause for DOM update

        more_button.click()
        page.wait_for_timeout(500)
        yield "Clicked 'More' button."
        page.wait_for_timeout(500)

        yield "Waiting for and clicking 'Export' button..."
        export_button = page.locator('li[export-leads="export-leads"]')
        page.wait_for_timeout(500)
        
        vortex_csv_filename = "daily_expireds.csv"
        vortex_csv_path = DOWNLOAD_DIR / vortex_csv_filename

        # Pre-emptively remove old file to ensure a clean check
        if vortex_csv_path.exists():
            vortex_csv_path.unlink()

        try:
            with page.expect_download(timeout=60000) as download_info:
                export_button.click()
            download = download_info.value
            download.save_as(vortex_csv_path)
            yield f"SUCCESS: Download event detected and file saved to {vortex_csv_path}"

        except PlaywrightTimeoutError:
            yield "WARNING: Download event was not detected in 60 seconds. Verifying file on disk..."
            # Fallback: Check if the file was downloaded anyway despite the timeout.
            time.sleep(5) # Give a few extra seconds for the write to complete
            if vortex_csv_path.is_file() and vortex_csv_path.stat().st_size > 0:
                yield f"SUCCESS: Verified file exists at {vortex_csv_path}."
                pass # The file exists, so we can proceed successfully.
            else:
                yield "ERROR: Verification failed. File not found on disk after timeout."
                raise # The download truly failed, so re-raise the timeout error.

        page.wait_for_timeout(500)

        # --- Part 2: Transform CSV ---
        for message in transform_vortex_to_boldtrail_csv(vortex_csv_path, SOURCE_NAME):
            if "boldtrail_csv_path" in message:
                boldtrail_csv_path = message["boldtrail_csv_path"]
            else:
                yield message

        # --- Part 3: Upload to Boldtrail ---
        for message in upload_csv_to_boldtrail(page, boldtrail_csv_path, SOURCE_NAME):
            yield message

        # If we get here, all steps are done
        yield "__DONE__"

    except PlaywrightTimeoutError as e:
        error_message = f"Timeout error during migration for '{SOURCE_NAME}': {e}"
        yield f"ERROR: {error_message}"
    except Exception as e:
        error_message = f"An unexpected error occurred during migration for '{SOURCE_NAME}': {e}"
        yield f"ERROR: {error_message}"
    finally:
        yield "Migration process finished. Closing resources."
        if page: page.close()
        if context: context.close()
        if browser: browser.close()
        if playwright: playwright.stop() 

if __name__ == "__main__":
    from email_reporter import send_report
    import pandas as pd
    import traceback
    import time

    print("VortexSync Daily Expireds Migration: Started")

    max_attempts = 3
    final_success = False
    final_log_messages = []
    final_error_details = ""

    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Starting Attempt {attempt} of {max_attempts} ---")
        
        log_messages_for_this_attempt = []
        attempt_success = False
        
        try:
            migration_generator = run_expired_migration()
            for message in migration_generator:
                print(message)
                log_messages_for_this_attempt.append(str(message))

            if any("Import process appears to be complete." in msg for msg in log_messages_for_this_attempt):
                attempt_success = True
                final_success = True
                final_log_messages.extend(log_messages_for_this_attempt)
                print(f"--- Attempt {attempt} was successful! ---")
                break # Exit the loop on success
            else:
                final_error_details = next((line for line in log_messages_for_this_attempt if line.startswith("ERROR:")), "Unknown error: Migration did not complete.")
                final_log_messages.extend(log_messages_for_this_attempt)
                final_log_messages.append("-" * 20) # Separator for logs between attempts

        except Exception as e:
            print(f"FATAL ERROR: A critical exception occurred on attempt {attempt}: {e}")
            final_error_details = traceback.format_exc()
            final_log_messages.extend(log_messages_for_this_attempt)
            final_log_messages.append(final_error_details)
            final_log_messages.append("-" * 20)
        
        if not attempt_success and attempt < max_attempts:
            print(f"--- Attempt {attempt} failed. Retrying in 30 seconds... ---")
            time.sleep(30)

    # --- Email Reporting ---
    print("\n--- Preparing Final Email Report ---")
    
    lead_count = 0
    lead_names = []
    boldtrail_csv_path = DOWNLOAD_DIR / "boldtrail_upload.csv"
    
    if boldtrail_csv_path.exists():
        try:
            df = pd.read_csv(boldtrail_csv_path)
            if 'first_name' in df.columns and 'last_name' in df.columns:
                lead_names = (df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')).str.strip().tolist()
                lead_names = [name for name in lead_names if name]
                lead_count = len(lead_names)
        except Exception as e:
            final_log_messages.append(f"Could not read details from boldtrail_upload.csv: {e}")

    if final_success:
        subject = f"✅ VortexSync Success: {lead_count} Expired Leads Migrated"
        body = (
            f"The daily Vortex -> Boldtrail migration for 'Daily Expireds' completed successfully.\n\n"
            f"Leads Transferred: {lead_count}\n\n"
        )
        if lead_names:
            body += "--- Migrated Leads ---\n" + "\n".join(lead_names) + "\n\n"
    else:
        subject = f"❌ VortexSync Failure: Migration Failed After {max_attempts} Attempts"
        body = (
            f"The daily Vortex -> Boldtrail migration failed after {max_attempts} attempts.\n\n"
            f"--- Final Error Details ---\n{final_error_details}\n\n"
        )
        # Add special context if the failure was the specific download timeout
        if "waiting for event \"download\"" in final_error_details:
            body += (
                "**Important Note:** This specific timeout error often occurs when there are no 'Daily Expireds' available to download. "
                "Please verify on the Vortex website if this failure repeats.\n\n"
            )

    body += "--- Full Log (All Attempts) ---\n" + "\n".join(final_log_messages)
    
    send_report(subject, body)
    
    print("\nVortexSync Daily Expireds Migration: Finished") 
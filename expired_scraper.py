import os
import sys

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
        
        # Always launch headless in the container, this is the most reliable way.
        browser = playwright.chromium.launch(headless=True)
        
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
        page.wait_for_selector("text=MY FOLDERS", timeout=60000)
        page.wait_for_timeout(500)
        yield "Dashboard loaded successfully."
        page.wait_for_timeout(500)

        yield f"Searching for and clicking on filter: '{SOURCE_NAME}'..."
        expired_filter_selector = f"div.folder-item-text:has-text('{SOURCE_NAME}')"
        page.locator(expired_filter_selector).click()
        page.wait_for_timeout(500)
        yield f"Clicked filter: '{SOURCE_NAME}'."
        yield "Waiting for lead data to finish loading..."
        page.wait_for_load_state('networkidle', timeout=90000)
        yield "Lead data loaded."
        page.wait_for_timeout(1000)

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
        
        yield "Checking for and removing potential chat widgets..."
        page.evaluate("document.querySelector('#intercom-container')?.remove()")
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

        with page.expect_download() as download_info:
            export_button.click()
        download = download_info.value
        page.wait_for_timeout(500)
        download.save_as(vortex_csv_path)
        page.wait_for_timeout(500)
        
        yield f"SUCCESS: File downloaded to {vortex_csv_path}"
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

    print("VortexSync Daily Expireds Migration: Started")
    
    log_messages = []
    success = False
    error_details = ""
    
    try:
        migration_generator = run_expired_migration()
        for message in migration_generator:
            print(message)
            log_messages.append(str(message))

        # Check for the success marker in the logs
        if any("Import process appears to be complete." in msg for msg in log_messages):
            success = True
        else:
            # Find the first ERROR message if success marker isn't found
            error_line = next((line for line in log_messages if line.startswith("ERROR:")), "Unknown error: Migration did not complete.")
            error_details = error_line

    except Exception as e:
        success = False
        print(f"FATAL ERROR: A critical exception occurred: {e}")
        error_details = traceback.format_exc()
        log_messages.append(error_details)

    # --- Email Reporting ---
    print("\n--- Preparing Email Report ---")
    
    lead_count = 0
    lead_names = []
    boldtrail_csv_path = DOWNLOAD_DIR / "boldtrail_upload.csv"
    
    # Try to read lead info, even on failure, as the file might exist
    if boldtrail_csv_path.exists():
        try:
            df = pd.read_csv(boldtrail_csv_path)
            # Ensure columns exist before trying to access them
            if 'first_name' in df.columns and 'last_name' in df.columns:
                lead_names = (df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')).str.strip().tolist()
                lead_names = [name for name in lead_names if name] # Filter out empty names
                lead_count = len(lead_names)
        except Exception as e:
            log_messages.append(f"Could not read details from boldtrail_upload.csv: {e}")

    # Build Email Subject and Body
    if success:
        subject = f"✅ VortexSync Success: {lead_count} Expired Leads Migrated"
        body = (
            f"The daily Vortex -> Boldtrail migration for 'Daily Expireds' completed successfully.\n\n"
            f"Leads Transferred: {lead_count}\n\n"
        )
        if lead_names:
            body += "--- Migrated Leads ---\n" + "\n".join(lead_names) + "\n\n"
    else:
        subject = f"❌ VortexSync Failure: Migration Failed"
        body = (
            f"The daily Vortex -> Boldtrail migration for 'Daily Expireds' encountered an error.\n\n"
            f"--- Error Details ---\n{error_details}\n\n"
        )

    body += "--- Full Log ---\n" + "\n".join(log_messages)
    
    # Send the final report
    send_report(subject, body)
    
    print("\nVortexSync Daily Expireds Migration: Finished") 
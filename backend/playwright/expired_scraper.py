import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import pathlib
from backend.playwright.boldtrail_utils import transform_vortex_to_boldtrail_csv, upload_csv_to_boldtrail

VORTEX_LOGIN_URL = "https://vortex.theredx.com/login"
DOWNLOAD_DIR = pathlib.Path(__file__).resolve().parent.parent / "cache" / "downloads"
SOURCE_NAME = "Daily Expireds" # Define the source for logging and notes

def run_expired_migration():
    """
    Orchestrates the migration of 'Daily Expireds' from Vortex to Boldtrail.
    Yields log messages as it progresses.
    """
    # Check if running in the Fly.io environment
    is_production = 'FLY_APP_NAME' in os.environ
    
    # Launch Playwright
    try:
        yield "Starting migration for: Daily Expireds"
        load_dotenv()
        DOWNLOAD_DIR.mkdir(exist_ok=True)
        
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
        
        yield "Entering credentials and logging in..."
        page.wait_for_timeout(1000) 
        page.keyboard.press("Tab")
        page.keyboard.type(os.getenv("VORTEX_USER"))
        page.keyboard.press("Tab")
        page.keyboard.type(os.getenv("VORTEX_PASS"))
        page.keyboard.press("Enter")

        yield "Waiting for dashboard to load..."
        page.wait_for_selector("text=MY FOLDERS", timeout=60000)
        yield "Dashboard loaded successfully."

        yield f"Searching for and clicking on filter: '{SOURCE_NAME}'..."
        expired_filter_selector = f"div.folder-item-text:has-text('{SOURCE_NAME}')"
        page.locator(expired_filter_selector).click()
        yield f"Clicked filter: '{SOURCE_NAME}'."
        page.wait_for_timeout(1000)

        yield "Waiting for and clicking 'Select All' checkbox..."
        select_all_checkbox = page.locator("#vxtb-button-check")
        select_all_checkbox.wait_for(state="visible", timeout=30000)
        select_all_checkbox.click()
        yield "Clicked 'Select All'."
        page.wait_for_timeout(1000)

        yield "Waiting for and clicking 'More' button..."
        more_button = page.locator('div.top-navbar__more-button:has-text("More")')
        more_button.wait_for(state="visible", timeout=30000)
        more_button.click()
        yield "Clicked 'More' button."

        yield "Waiting for and clicking 'Export' button..."
        export_button = page.locator('li[export-leads="export-leads"]')
        
        vortex_csv_filename = "daily_expireds.csv"
        vortex_csv_path = DOWNLOAD_DIR / vortex_csv_filename

        with page.expect_download() as download_info:
            export_button.click()
        download = download_info.value
        download.save_as(vortex_csv_path)
        
        yield f"SUCCESS: File downloaded to {vortex_csv_path}"

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
    from backend.email_reporter import send_report
    from dotenv import load_dotenv
    import os
    import re
    import traceback
    import multiprocessing

    # Load .env file for local execution and for production secrets
    load_dotenv()

    print("VortexSync Daily Expireds Migration: Started")

    log_messages = []
    lead_count = 0
    success = False
    error_info = None

    try:
        migration_generator = run_expired_migration()
        for message in migration_generator:
            # The __DONE__ message is for the web UI, not needed for the script log
            if message == "__DONE__":
                continue
            
            print(message)  # This will go to fly logs
            log_messages.append(str(message))
            
            # Dynamically extract lead count
            if "SUCCESS: Transformed" in message:
                match = re.search(r'(\d+)', message)
                if match:
                    lead_count = int(match.group(1))

        # The process is successful if the final upload message is in the logs
        if any("Import process appears to be complete." in msg for msg in log_messages):
            success = True
        else:
            error_info = "Migration process did not complete the final upload step. Check logs for details."

    except Exception as e:
        print(f"ERROR: An exception occurred: {e}")
        # Capture the full traceback for detailed error reporting
        error_info = traceback.format_exc()
        log_messages.append(error_info)
        success = False

    # --- Email Reporting ---
    print("VortexSync: Preparing email report...")
    if success:
        subject = f"✅ VortexSync Success: {lead_count} Expired Leads Migrated"
        body = (
            f"The daily Vortex -> Boldtrail migration for 'Daily Expireds' completed successfully.\n\n"
            f"Leads Uploaded: {lead_count}\n\n"
            f"Have a great day!"
        )
    else:
        subject = "❌ VortexSync FAILURE: Daily Expireds Migration Failed"
        body = (
            f"The daily Vortex -> Boldtrail migration for 'Daily Expireds' failed.\n\n"
            f"Leads Processed Before Failure: {lead_count}\n\n"
            f"--- ERROR ---\n{error_info}\n\n"
            f"--- FULL LOGS ---\n" + "\n".join(log_messages)
        )

    try:
        # Only send a report if email credentials are configured
        if all(k in os.environ for k in ["EMAIL_USER", "EMAIL_PASS", "EMAIL_TO", "EMAIL_HOST", "EMAIL_PORT"]):
            print("VortexSync: Attempting to send email report (30s timeout)...")
            
            # Use multiprocessing for a reliable cross-platform timeout
            process = multiprocessing.Process(target=send_report, args=(subject, body))
            process.start()
            process.join(30) # Wait for 30 seconds

            if process.is_alive():
                process.terminate() # Terminate the hanging process
                process.join() # Clean up
                raise TimeoutError("Email sending timed out after 30 seconds.")
            
            if process.exitcode != 0:
                raise RuntimeError("Email sending process failed with an error.")

            print("VortexSync: Email report sent successfully.")
        else:
            print("VortexSync: Email credentials not found, skipping email report.")
    except TimeoutError as e:
        print(f"VortexSync: CRITICAL - FAILED TO SEND EMAIL REPORT: {e}")
    except Exception as e:
        print(f"VortexSync: CRITICAL - FAILED TO SEND EMAIL REPORT: {traceback.format_exc()}")

    print("VortexSync Daily Expireds Migration: Finished") 
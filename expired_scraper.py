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
    # Simplified for direct execution and testing.
    # The script will now run once and print all its progress to the console.
    print("VortexSync Daily Expireds Migration: Started")
    migration_generator = run_expired_migration()
    for message in migration_generator:
        print(message)
    print("VortexSync Daily Expireds Migration: Finished") 
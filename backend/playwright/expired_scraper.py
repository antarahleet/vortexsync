from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import os
import pathlib
from backend.utils.logger import log
from backend.playwright.boldtrail_utils import transform_vortex_to_boldtrail_csv, upload_csv_to_boldtrail

VORTEX_LOGIN_URL = "https://vortex.theredx.com/login"
DOWNLOAD_DIR = pathlib.Path(__file__).resolve().parent.parent / "cache" / "downloads"
SOURCE_NAME = "Daily Expireds" # Define the source for logging and notes

def run_expired_migration():
    """
    Orchestrates the migration of 'Daily Expireds' from Vortex to Boldtrail.
    """
    print(f"Starting migration for: {SOURCE_NAME}")
    load_dotenv()
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--start-maximized"])
            context = browser.new_context(accept_downloads=True, no_viewport=True)
            page = context.new_page()

            # --- Part 1: Download from Vortex ---
            print("Navigating to Vortex login page...")
            page.goto(VORTEX_LOGIN_URL, timeout=60000)
            
            print("Entering credentials and logging in...")
            page.wait_for_timeout(1000) # Wait for page to settle
            page.keyboard.press("Tab")
            page.keyboard.type(os.getenv("VORTEX_USER"))
            page.keyboard.press("Tab")
            page.keyboard.type(os.getenv("VORTEX_PASS"))
            page.keyboard.press("Enter")

            print("Waiting for dashboard to load...")
            page.wait_for_selector("text=MY FOLDERS", timeout=60000)
            print("Dashboard loaded successfully.")

            print(f"Searching for and clicking on filter: '{SOURCE_NAME}'...")
            expired_filter_selector = f"div.folder-item-text:has-text('{SOURCE_NAME}')"
            page.locator(expired_filter_selector).click()
            print(f"Clicked filter: '{SOURCE_NAME}'.")
            page.wait_for_timeout(1000) # Pause for 1 second as requested

            print("Waiting for and clicking 'Select All' checkbox...")
            select_all_checkbox = page.locator("#vxtb-button-check")
            select_all_checkbox.wait_for(state="visible", timeout=30000)
            select_all_checkbox.click()
            print("Clicked 'Select All'.")
            page.wait_for_timeout(1000) # Pause for 1 second as requested

            print("Waiting for and clicking 'More' button...")
            more_button = page.locator('div.top-navbar__more-button:has-text("More")')
            more_button.wait_for(state="visible", timeout=30000)
            more_button.click()
            print("Clicked 'More' button.")

            print("Waiting for and clicking 'Export' button...")
            export_button = page.locator('li[export-leads="export-leads"]')
            
            vortex_csv_filename = "daily_expireds.csv"
            vortex_csv_path = DOWNLOAD_DIR / vortex_csv_filename

            with page.expect_download() as download_info:
                export_button.click()
            download = download_info.value
            download.save_as(vortex_csv_path)
            
            print(f"SUCCESS: File downloaded to {vortex_csv_path}")
            log("vortex_csv_downloaded", {"source": SOURCE_NAME, "path": str(vortex_csv_path)})

            # --- Part 2: Transform CSV ---
            transform_result = transform_vortex_to_boldtrail_csv(vortex_csv_path, SOURCE_NAME)
            if transform_result["status"] == "error":
                raise Exception(transform_result["message"])

            boldtrail_csv_path = pathlib.Path(transform_result["boldtrail_csv_path"])

            # --- Part 3: Upload to Boldtrail ---
            upload_result = upload_csv_to_boldtrail(page, boldtrail_csv_path, SOURCE_NAME)
            if upload_result["status"] == "error":
                raise Exception(upload_result["message"])

            print("Closing browser context.")
            context.close()
            browser.close()
            return upload_result

    except PlaywrightTimeoutError as e:
        error_message = f"Timeout error during migration for '{SOURCE_NAME}': {e}"
        print(f"ERROR: {error_message}")
        log("migration_error", {"source": SOURCE_NAME, "error": str(e)})
        return {"status": "error", "message": error_message}
    except Exception as e:
        error_message = f"An unexpected error occurred during migration for '{SOURCE_NAME}': {e}"
        print(f"ERROR: {error_message}")
        log("migration_error", {"source": SOURCE_NAME, "error": str(e)})
        return {"status": "error", "message": error_message} 
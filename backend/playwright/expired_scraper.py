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
    Yields log messages as it progresses.
    """
    yield f"Starting migration for: {SOURCE_NAME}"
    load_dotenv()
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    
    page = None
    context = None
    browser = None
    playwright = None

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(accept_downloads=True, no_viewport=True)
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
        log("vortex_csv_downloaded", {"source": SOURCE_NAME, "path": str(vortex_csv_path)})

        # --- Part 2: Transform CSV ---
        for message in transform_vortex_to_boldtrail_csv(vortex_csv_path, SOURCE_NAME):
            if "boldtrail_csv_path" in message:
                boldtrail_csv_path = message["boldtrail_csv_path"]
            else:
                yield message

        # --- Part 3: Upload to Boldtrail ---
        for message in upload_csv_to_boldtrail(page, boldtrail_csv_path, SOURCE_NAME):
            yield message

    except PlaywrightTimeoutError as e:
        error_message = f"Timeout error during migration for '{SOURCE_NAME}': {e}"
        yield f"ERROR: {error_message}"
        log("migration_error", {"source": SOURCE_NAME, "error": str(e)})
    except Exception as e:
        error_message = f"An unexpected error occurred during migration for '{SOURCE_NAME}': {e}"
        yield f"ERROR: {error_message}"
        log("migration_error", {"source": SOURCE_NAME, "error": str(e)})
    finally:
        yield "Migration process finished. Closing resources."
        if page: page.close()
        if context: context.close()
        if browser: browser.close()
        if playwright: playwright.stop() 
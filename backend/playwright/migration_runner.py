from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import os
import pathlib
from backend.utils.logger import log
from backend.playwright.boldtrail_utils import transform_vortex_to_boldtrail_csv, upload_csv_to_boldtrail

VORTEX_LOGIN_URL = "https://vortex.theredx.com/login"
DOWNLOAD_DIR = pathlib.Path(__file__).resolve().parent.parent / "cache" / "downloads"

def run_migration(folder_name: str):
    """
    Main function to orchestrate the lead migration for a specific folder.
    """
    print(f"Starting migration for folder: {folder_name}")
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
            # Using robust keyboard navigation for login
            page.wait_for_timeout(1000) # Wait for page to settle
            page.keyboard.press("Tab")
            page.keyboard.type(os.getenv("VORTEX_USER"))
            page.keyboard.press("Tab")
            page.keyboard.type(os.getenv("VORTEX_PASS"))
            page.keyboard.press("Enter")

            print("Waiting for dashboard to load...")
            page.wait_for_selector("text=MY FOLDERS", timeout=60000)
            print("Dashboard loaded successfully.")

            print(f"Searching for and clicking on folder: '{folder_name}'...")
            # Using the same proven container logic from the folder_scraper.py
            my_folders_header = page.locator('span.title:has-text("MY FOLDERS")')
            my_folders_container = my_folders_header.locator("xpath=../..")

            # Now find the specific folder link *within that correct container*
            folder_selector = f".folder-item-text:has-text('{folder_name}')"
            folder_to_click = my_folders_container.locator(folder_selector)
            
            print(f"Waiting for folder '{folder_name}' to be visible and clicking it.")
            # Explicitly scroll the element into view before clicking.
            folder_to_click.scroll_into_view_if_needed(timeout=30000)
            folder_to_click.click()
            print(f"Clicked folder: '{folder_name}'.")
            page.wait_for_timeout(1000) # Pause for 1 second as requested

            print("Waiting for and clicking 'Select All' checkbox...")
            select_all_checkbox = page.locator("#vxtb-button-check")
            select_all_checkbox.wait_for(state="visible", timeout=30000)
            select_all_checkbox.click()
            print("Clicked 'Select All'.")
            page.wait_for_timeout(1000) # Pause for 1 second as requested

            print("Waiting for and clicking 'div.top-navbar__more-button:has-text(\"More\")'...")
            more_button = page.locator('div.top-navbar__more-button:has-text("More")')
            more_button.wait_for(state="visible", timeout=30000)
            more_button.click()
            print("Clicked 'More' button.")

            print("Waiting for and clicking 'li[export-leads=\"export-leads\"]'...")
            export_button = page.locator('li[export-leads="export-leads"]')
            
            sanitized_folder_name = "".join(x for x in folder_name if x.isalnum() or x in " _-").replace(" ", "_")
            vortex_csv_filename = f"{sanitized_folder_name}.csv"
            vortex_csv_path = DOWNLOAD_DIR / vortex_csv_filename

            with page.expect_download() as download_info:
                export_button.click()
            download = download_info.value
            download.save_as(vortex_csv_path)
            
            print(f"SUCCESS: File downloaded to {vortex_csv_path}")
            log("vortex_csv_downloaded", {"folder": folder_name, "path": str(vortex_csv_path)})

            # --- Part 2: Transform CSV ---
            transform_result = transform_vortex_to_boldtrail_csv(vortex_csv_path, folder_name)
            if transform_result["status"] == "error":
                raise Exception(transform_result["message"])

            boldtrail_csv_path = transform_result["boldtrail_csv_path"]

            # --- Part 3: Upload to Boldtrail ---
            upload_result = upload_csv_to_boldtrail(page, boldtrail_csv_path, folder_name)
            if upload_result["status"] == "error":
                raise Exception(upload_result["message"])

            print("Closing browser context.")
            context.close()
            browser.close()
            return upload_result

    except PlaywrightTimeoutError as e:
        error_message = f"Timeout error during migration for '{folder_name}': {e}"
        print(f"ERROR: {error_message}")
        log("migration_error", {"folder": folder_name, "error": str(e)})
        return {"status": "error", "message": error_message}
    except Exception as e:
        error_message = f"An unexpected error occurred during migration for '{folder_name}': {e}"
        print(f"ERROR: {error_message}")
        log("migration_error", {"folder": folder_name, "error": str(e)})
        return {"status": "error", "message": error_message} 
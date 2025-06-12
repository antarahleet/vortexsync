from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os, json, pathlib
from backend.utils.logger import log

CACHE = pathlib.Path(__file__).resolve().parent.parent / "cache/folders.json"

# FIXME: Replace with the actual Vortex login URL
VORTEX_LOGIN_URL = "https://vortex.theredx.com/login" 

def scrape_folders():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(VORTEX_LOGIN_URL)
        
        # Use keyboard navigation as suggested by the user
        page.keyboard.press("Tab")
        page.keyboard.type(os.getenv("VORTEX_USER"))
        page.keyboard.press("Tab")
        page.keyboard.type(os.getenv("VORTEX_PASS"))
        page.keyboard.press("Enter")

        # Wait for the "MY FOLDERS" header to appear.
        my_folders_header_selector = 'span.title:has-text("MY FOLDERS")'
        page.wait_for_selector(my_folders_header_selector)

        # Find the parent container of the "MY FOLDERS" header, which should hold the folder list.
        # This locator finds the header, then goes up two levels in the HTML tree, which is
        # likely the container for the entire "MY FOLDERS" collapsible panel.
        folder_container = page.locator(my_folders_header_selector).locator("..").locator("..")

        # Find all folder elements within that specific container.
        folder_elements = folder_container.locator(".folder-item-text").all()
        
        folders = [el.inner_text().strip() for el in folder_elements]
        
        # Use list(dict.fromkeys(...)) to remove duplicates while preserving order
        unique_folders = list(dict.fromkeys(folders))
        
        CACHE.write_text(json.dumps(unique_folders, indent=2))
        log("folders_updated", {"count": len(unique_folders)})
        ctx.close(); browser.close()
        return unique_folders

if __name__ == "__main__":
    print("Scraping folders from Vortex...")
    scraped_folders = scrape_folders()
    print("Scraping complete.")
    print(f"Found {len(scraped_folders)} folders:")
    print(json.dumps(scraped_folders, indent=2)) 
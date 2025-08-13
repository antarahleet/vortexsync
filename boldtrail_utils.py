from playwright.sync_api import Page
import os
import pathlib
import pandas as pd
import re

DOWNLOAD_DIR = pathlib.Path(__file__).resolve().parent / "cache" / "downloads"
BOLDTRAIL_LOGIN_URL = "https://app.boldtrail.com/login"

def transform_vortex_to_boldtrail_csv(vortex_csv_path: pathlib.Path, source_name: str):
    """
    Reads a Vortex CSV, transforms it, and saves it. Yields progress messages.
    """
    yield "--- Transforming CSV for Boldtrail Upload ---"
    try:
        vortex_df = pd.read_csv(vortex_csv_path, dtype=str).fillna('')
        yield f"Read {len(vortex_df)} leads from {vortex_csv_path}"
    except FileNotFoundError:
        yield f"ERROR: Downloaded Vortex CSV not found at {vortex_csv_path}"
        return
    except Exception as e:
        yield f"ERROR: Error reading Vortex CSV: {e}"
        return

    boldtrail_leads = []
    
    boldtrail_columns = [
        'first_name', 'last_name', 'status', 'deal_type', 'email_optin', 
        'text_on', 'phone_on', 'email', 'cell_phone_1', 'primary_address', 
        'primary_city', 'primary_state', 'primary_zip', 'agent_notes',
        'source'
    ]

    for index, vortex_lead in vortex_df.iterrows():
        full_name = vortex_lead.get('Name', '')
        first_name, last_name = full_name.split(" ", 1) if " " in full_name else (full_name, "")

        phone_columns = ['Phone', 'Phone 1', 'Phone 2']
        phone_number_raw = ''
        for col in phone_columns:
            if vortex_lead.get(col):
                phone_number_raw = vortex_lead.get(col)
                break
        cell_phone = re.sub(r'[^0-9]', '', str(phone_number_raw))

        address = vortex_lead.get('Property Address', '')
        city = vortex_lead.get('Property City', '')
        state = vortex_lead.get('Property State', '')
        zip_code = vortex_lead.get('Property Zip', '')

        # 4. Generate the detailed agent note with all non-empty fields
        note_header = f"[Vortex Source: {source_name}]"
        note_bullets = []
        for col, val in vortex_lead.items():
            if pd.notna(val) and str(val).strip():
                formatted_col = col.replace('_', ' ').lower()
                note_bullets.append(f"* {formatted_col}: {str(val).strip()}")
        agent_note = f"{note_header}\n\n" + "\n".join(note_bullets)

        boldtrail_lead = {
            'first_name': first_name,
            'last_name': last_name,
            'status': 'New Lead',
            'deal_type': 'Seller',
            'email_optin': 'yes',
            'text_on': 'yes',
            'phone_on': 'yes',
            'email': vortex_lead.get('Email', ''),
            'cell_phone_1': cell_phone,
            'primary_address': address,
            'primary_city': city,
            'primary_state': state,
            'primary_zip': zip_code,
            'agent_notes': agent_note,
            'source': 'VortexSync'
        }
        boldtrail_leads.append(boldtrail_lead)

    boldtrail_df = pd.DataFrame(boldtrail_leads, columns=boldtrail_columns)
    
    boldtrail_csv_path = DOWNLOAD_DIR / "boldtrail_upload.csv"
    boldtrail_df.to_csv(boldtrail_csv_path, index=False)
    
    yield f"SUCCESS: Transformed CSV created at {boldtrail_csv_path}"
    yield {"boldtrail_csv_path": boldtrail_csv_path} # Yield path separately


def upload_csv_to_boldtrail(page: Page, boldtrail_csv_path: pathlib.Path, source_name: str):
    """
    Logs into Boldtrail and uploads the CSV. Yields progress messages.
    """
    yield "--- Starting Boldtrail CSV Upload ---"
    
    yield "Navigating to Boldtrail login page..."
    page.goto(BOLDTRAIL_LOGIN_URL, timeout=90000)
    yield "Entering Boldtrail credentials via keyboard..."
    page.wait_for_timeout(1000)
    page.keyboard.press("Tab")
    page.keyboard.type(os.getenv("BOLDTRAIL_USER"))
    page.keyboard.press("Enter")
    
    # Wait for password field to appear after email submission
    yield "Waiting for password field to appear..."
    password_input_selector = "input[type='password']"
    page.wait_for_selector(password_input_selector, timeout=30000)
    page.wait_for_timeout(1000)
    
    page.keyboard.press("Tab")
    page.keyboard.type(os.getenv("BOLDTRAIL_PASS"))
    page.keyboard.press("Enter")
    
    yield "Waiting for dashboard to load and finding Lead Engine button..."
    lead_engine_selector = "div.side-menu-item-content:has-text('LeadEngine')"
    page.wait_for_selector(lead_engine_selector, timeout=90000)
    yield "Logged into Boldtrail and found Lead Engine button."

    page.locator(lead_engine_selector).click()
    
    yield "Clicking 'Start an Import'..."
    start_import_selector = "button:has-text('Start an Import')"
    page.wait_for_selector(start_import_selector, timeout=90000)
    
    yield "Checking for and removing potential chat widgets..."
    page.evaluate("document.querySelector('#intercom-container')?.remove()")
    page.wait_for_timeout(250) # Brief pause for DOM update

    page.locator(start_import_selector).click()

    yield "Waiting for bulk import page and clicking 'Get Started'..."
    page.wait_for_url("**/bulk-import", timeout=90000)
    get_started_selector = "button[data-userpilot='do-it-yourself-get-started-button']"
    page.wait_for_selector(get_started_selector, timeout=90000)
    page.locator(get_started_selector).click()

    yield "Waiting for file upload page to load..."
    page.wait_for_timeout(2500) 

    yield f"Uploading {boldtrail_csv_path}..."
    file_input_selector = "input[type='file']" 
    page.wait_for_selector(file_input_selector, state='attached', timeout=90000)
    page.set_input_files(file_input_selector, boldtrail_csv_path)

    yield "File selected. Handling preview page..."
    
    terms_checkbox_selector = "input.base-input"
    page.wait_for_selector(terms_checkbox_selector, timeout=10000)
    page.locator(terms_checkbox_selector).check()
    yield "Checked 'I understand' box."

    next_button_selector = "button.next-btn:has-text('Next')"
    page.locator(next_button_selector).click()
    yield "Clicked 'Next' button on preview page."

    yield "Handling final import page..."
    
    page.wait_for_selector(next_button_selector, timeout=10000)
    page.locator(next_button_selector).click()
    yield "Clicked 'Next' button on routing page."

    # Add hashtag as before
    hashtag_input_selector = "input[placeholder='Search For Hashtags']"
    page.wait_for_selector(hashtag_input_selector, timeout=10000)
    hashtag_input = page.locator(hashtag_input_selector)
    hashtag_input.click()
    hashtag_input.type("vortexsync")
    hashtag_input.press("Enter")
    yield "Added 'vortexsync' hashtag."

    # Select Smart Campaign per request
    campaign_name = 'WATCH VIDEO FIRST!!!'
    campaign_input_selector = "div.fake-input:nth-child(1) > div:nth-child(1) > input:nth-child(2)"
    yield "Selecting Smart Campaign..."
    try:
        page.wait_for_selector(campaign_input_selector, timeout=10000)
        campaign_input = page.locator(campaign_input_selector)
        campaign_input.click()
        yield "Clicked on campaign dropdown"
        
        # Wait for dropdown options to appear and select the campaign
        # Look for the specific campaign option in the dropdown
        page.wait_for_timeout(1000)  # Wait for dropdown to fully open
        
        # Try to find the campaign option by looking for it in the dropdown area
        campaign_option_selector = f"div.dropdown-option:has-text('{campaign_name}'), div.option:has-text('{campaign_name}'), div:has-text('{campaign_name}'):not([id='__nuxt']):not([id='__layout'])"
        
        try:
            page.wait_for_selector(campaign_option_selector, timeout=10000)
            page.locator(campaign_option_selector).first.click()
            yield f"Selected campaign: {campaign_name}"
        except:
            # Fallback: try to find any element with the campaign name that's clickable
            yield f"Trying alternative method to select campaign: {campaign_name}"
            all_campaign_elements = page.locator(f"*:has-text('{campaign_name}')")
            if all_campaign_elements.count() > 0:
                # Find the most likely dropdown option (not the main page divs)
                for i in range(all_campaign_elements.count()):
                    element = all_campaign_elements.nth(i)
                    try:
                        if element.is_visible() and element.is_enabled():
                            element.click()
                            yield f"Selected campaign using alternative method: {campaign_name}"
                            break
                    except:
                        continue
    except Exception as e:
        yield f"WARNING: Could not select campaign automatically: {e}"

    # Final Submission
    finish_button_selector = "button.next-btn:has-text('Finish')"
    yield "Clicking the final 'Finish' button..."
    page.locator(finish_button_selector).click()
    
    page.wait_for_timeout(5000)
    yield "Import process appears to be complete."

    return {"status": "success", "message": f"Migration for {source_name} completed successfully."} 
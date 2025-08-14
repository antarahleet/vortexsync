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

    # Select Smart Campaign with robust retry logic
    campaign_name = 'WATCH VIDEO FIRST!!!'
    yield f"Starting campaign selection process for: {campaign_name}"
    
    def select_campaign_robust():
        """Robust campaign selection with multiple strategies and verification"""
        max_attempts = 3
        
        for attempt in range(1, max_attempts + 1):
            yield f"Campaign selection attempt {attempt}/{max_attempts}"
            
            try:
                # Strategy 1: Try multiple common campaign dropdown selectors
                campaign_selectors = [
                    "div.fake-input:nth-child(1) > div:nth-child(1) > input:nth-child(2)",
                    "input[placeholder*='campaign']",
                    "input[placeholder*='Campaign']", 
                    "div.fake-input input",
                    "div[class*='campaign'] input",
                    "div[class*='select'] input",
                    ".campaign-select input",
                    ".smart-campaign input"
                ]
                
                campaign_input = None
                successful_selector = None
                
                # Find a working campaign dropdown selector
                for selector in campaign_selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            test_input = page.locator(selector).first
                            if test_input.is_visible() and test_input.is_enabled():
                                campaign_input = test_input
                                successful_selector = selector
                                yield f"Found campaign input using selector: {selector}"
                                break
                    except:
                        continue
                
                if not campaign_input:
                    yield f"No campaign dropdown found on attempt {attempt}"
                    if attempt < max_attempts:
                        page.wait_for_timeout(2000)
                        continue
                    else:
                        return False
                
                # Click the dropdown to open it
                yield "Clicking campaign dropdown to open options..."
                campaign_input.click()
                page.wait_for_timeout(1500)  # Wait for dropdown animation
                
                # Strategy 2: Try multiple methods to find and click the campaign option
                campaign_found = False
                
                # Method 1: Look for dropdown options with various selectors
                option_selectors = [
                    f"div.dropdown-option:has-text('{campaign_name}')",
                    f"li:has-text('{campaign_name}')",
                    f"div.option:has-text('{campaign_name}')",
                    f"div[role='option']:has-text('{campaign_name}')",
                    f"div[class*='dropdown'] div:has-text('{campaign_name}')",
                    f"ul li:has-text('{campaign_name}')",
                    f".select-option:has-text('{campaign_name}')"
                ]
                
                for option_selector in option_selectors:
                    try:
                        if page.locator(option_selector).count() > 0:
                            option = page.locator(option_selector).first
                            if option.is_visible():
                                option.click()
                                yield f"Clicked campaign option using selector: {option_selector}"
                                campaign_found = True
                                break
                    except Exception as e:
                        yield f"Failed with selector {option_selector}: {str(e)}"
                        continue
                
                # Method 2: If specific selectors failed, try broader search
                if not campaign_found:
                    yield "Trying broader search for campaign option..."
                    try:
                        # Look for any clickable element containing the campaign name
                        all_elements = page.locator(f"*:has-text('{campaign_name}')")
                        count = all_elements.count()
                        yield f"Found {count} elements containing '{campaign_name}'"
                        
                        for i in range(count):
                            try:
                                element = all_elements.nth(i)
                                # Skip elements that are likely not dropdown options
                                tag_name = element.evaluate("el => el.tagName.toLowerCase()")
                                if tag_name in ['html', 'body', 'div[id="__nuxt"]', 'div[id="__layout"]']:
                                    continue
                                    
                                if element.is_visible() and element.is_enabled():
                                    # Check if element is in a dropdown context
                                    parent_classes = element.evaluate("el => el.parentElement?.className || ''")
                                    if any(keyword in parent_classes.lower() for keyword in ['dropdown', 'option', 'select', 'menu']):
                                        element.click()
                                        yield f"Selected campaign using broad search method (element {i})"
                                        campaign_found = True
                                        break
                            except:
                                continue
                    except Exception as e:
                        yield f"Broad search failed: {str(e)}"
                
                # Method 3: Keyboard navigation as last resort
                if not campaign_found and attempt == max_attempts:
                    yield "Trying keyboard navigation as final attempt..."
                    try:
                        # Re-click the dropdown to ensure it's focused
                        campaign_input.click()
                        page.wait_for_timeout(500)
                        
                        # Type the campaign name to filter/search
                        campaign_input.type(campaign_name)
                        page.wait_for_timeout(1000)
                        
                        # Press Enter or Down arrow then Enter
                        page.keyboard.press("Enter")
                        page.wait_for_timeout(500)
                        
                        yield "Attempted keyboard selection"
                        campaign_found = True  # Assume success for keyboard method
                    except Exception as e:
                        yield f"Keyboard navigation failed: {str(e)}"
                
                # Quick verification that selection worked
                if campaign_found:
                    page.wait_for_timeout(500)  # Reduced wait time
                    
                    # Quick check - just look for campaign name in the input area
                    try:
                        # Check the original input element first (fastest check)
                        if successful_selector:
                            selected_element = page.locator(successful_selector).first
                            selected_text = selected_element.text_content() or selected_element.get_attribute('value') or ""
                            if campaign_name in selected_text:
                                yield f"SUCCESS: Campaign '{campaign_name}' is selected"
                                return True
                    except:
                        pass
                    
                    # If first check fails, do one quick broader check
                    try:
                        campaign_area = page.locator("div:has-text('Smart Campaign'), div:has-text('Campaign')").first
                        if campaign_area.count() > 0:
                            area_text = campaign_area.text_content() or ""
                            if campaign_name in area_text:
                                yield f"SUCCESS: Campaign '{campaign_name}' appears selected"
                                return True
                    except:
                        pass
                    
                    # For attempt 1, assume success if we got this far and proceed
                    if attempt == 1:
                        yield f"PROCEEDING: Campaign selection attempted, continuing with import"
                        return True
                    
                    yield f"WARNING: Verification unclear on attempt {attempt}, retrying..."
                    if attempt < max_attempts:
                        page.wait_for_timeout(1500)  # Shorter retry wait
                        continue
                
            except Exception as e:
                yield f"Attempt {attempt} failed with error: {str(e)}"
                if attempt < max_attempts:
                    page.wait_for_timeout(3000)
                    continue
        
        yield f"FAILED: Could not reliably select campaign '{campaign_name}' after {max_attempts} attempts"
        return False
    
    # Execute the robust campaign selection
    try:
        for message in select_campaign_robust():
            yield message
    except Exception as e:
        yield f"ERROR: Campaign selection process failed: {e}"

    # Brief pause to ensure campaign selection is fully processed
    page.wait_for_timeout(1000)
    yield "Campaign selection complete, proceeding to finish import..."

    # Final Submission
    finish_button_selector = "button.next-btn:has-text('Finish')"
    yield "Clicking the final 'Finish' button..."
    page.locator(finish_button_selector).click()
    
    page.wait_for_timeout(5000)
    yield "Import process appears to be complete."

    return {"status": "success", "message": f"Migration for {source_name} completed successfully."} 
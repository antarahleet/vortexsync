# Cursor Development Log for VortexSync

This document logs the development and debugging steps taken to build the VortexSync application.

## 1. Project Scaffolding

- **Initial Setup**: Reviewed `cursor_build_instructions(1).md` and `vortex-boldtrail-prd.md` to understand project goals.
- **Directory Structure**: Created the backend directory structure (`/backend`, `/backend/cache`, `/backend/playwright`, `/backend/utils`).
- **File Creation**: Created all initial Python files as specified in the build guide:
    - `backend/app.py`
    - `backend/utils/logger.py`
    - `backend/playwright/folder_scraper.py`
    - `backend/playwright/migration_runner.py` (stub)
    - `backend/__init__.py`
    - `requirements.txt`
- **Frontend Scaffolding**: Initialized a Next.js project in the `/frontend` directory using TypeScript, the App Router, and Tailwind CSS.

## 2. Environment & Dependencies

- **Virtual Environment**: Encountered and resolved initial errors with `venv` creation on Windows.
- **Python Dependencies**: Installed `playwright`, `flask`, `pandas`, and `python-dotenv` from `requirements.txt`.
- **Browser Drivers**: Installed the required Chromium driver for Playwright.
- **`.env` File**: Created the `.env` file for storing credentials.

## 3. Backend & API Development

- **Flask Server**: Implemented the initial Flask server in `app.py` with routes for `/api/folders`, `/api/update-folders`, and `/api/run-migration`.
- **CORS Resolution**: Diagnosed a `NS_ERROR_CONNECTION_REFUSED` error. The root cause was the browser's Cross-Origin Resource Sharing (CORS) policy blocking requests from the frontend (`:3000`) to the backend (`:5000`).
    - **Solution**: Installed the `Flask-CORS` package and configured the Flask app to allow requests from any origin, resolving the connection issue.

## 4. Playwright Scraper Debugging

The core challenge was getting the `folder_scraper.py` script to work reliably. This involved a multi-step debugging process.

1.  **Initial Failure (`ERR_NAME_NOT_RESOLVED`)**: The initial login URL (`login.vortex.com`) was a placeholder and did not exist.
    - **Solution**: Updated the script with the correct URL: `https://vortex.theredx.com/login`.

2.  **Selector Timeouts (`TimeoutError`)**: The initial CSS selectors (`#email`, `#password`) were placeholders and did not match the live site. Subsequent attempts with dynamically generated IDs also failed.
    - **Solution**: Switched to a more robust keyboard-based navigation strategy (`Tab`, `Tab`, `Enter`). This proved to be the most reliable way to handle the dynamic login form.

3.  **Post-Login Timeout (`TimeoutError`)**: The script was initially waiting for the network to be "idle" after login, which never happened due to modern web app behavior (background pings, etc.).
    - **Solution**: Removed the `wait_for_load_state("networkidle")` call and replaced it with a `page.wait_for_selector()` call targeting the "MY FOLDERS" text on the dashboard. This ensured the script waited for a specific, meaningful element.

4.  **Credential Loading Issue**: The script worked when run directly from the terminal but failed to load the correct credentials when triggered by the Flask server (it defaulted to `you@example.com`).
    - **Diagnosis**: Determined this was an environment context issue. The Flask reloader was likely changing the working directory, causing `load_dotenv()` to fail silently.
    - **Solution**: Moved the `load_dotenv()` logic from `folder_scraper.py` to the main `app.py` entry point. This ensures that the environment variables are loaded reliably as soon as the application starts.

## 5. Frontend UI

- **API Utility**: Created `frontend/src/lib/api.ts` to centralize fetch requests to the backend.
- **Main Page**: Developed a functional UI in `frontend/src/app/page.tsx` with React state management to:
    - Display the list of folders in a dropdown.
    - Provide a button to trigger the folder update process.
    - Provide a button to start the migration (currently a stub).

## 6. UI Refinements & Final Touches

This phase focused on improving the user experience and the accuracy of the scraper.

1.  **Scraper Scope Refinement**: The scraper was initially capturing all folder-like elements, including unwanted filter items.
    - **Solution**: The Playwright script was modified to first locate the "MY FOLDERS" header element and then search for folder items *only within that parent container*. This dramatically improved the accuracy of the scraped list.

2.  **Preserving Folder Order**: The initial script returned folders in alphabetical order, not their original order from the website.
    - **Solution**: Changed the method of removing duplicates from `sorted(set(folders))` to `list(dict.fromkeys(folders))`, which preserves insertion order.

3.  **Loading Animation**: Added a loading spinner to the "Update Vortex Folders" button to provide visual feedback during the scraping process.

4.  **Interactive Progress Bar**: Implemented a sophisticated progress bar to replace the "Start Migration" button during the folder update process.
    - **Functionality**:
        - Animates over ~10 seconds, stopping at 99%.
        - Waits for both the timer to complete and the background API call to succeed.
        - On success, it jumps to 100%, displays the success message, and then reverts to the "Start Migration" button.
        - On failure, it immediately stops and reverts to the button, showing an error message.
    - **Layout Restoration**: After an accidental UI redesign during the progress bar implementation, the original layout (large title, button placement) was restored at the user's request, successfully merging the new functionality with the preferred design.

## Current Status

- The backend and frontend servers are running.
- The folder scraping logic is confirmed to be working correctly.
- The application should now be able to successfully update the folder list from the web interface.
- The backend and frontend servers are fully operational.
- The folder scraper is accurate and preserves the original folder order.
- The UI provides clear, interactive feedback during the folder update process with a timed progress bar.
- The application is complete according to the build instructions and ready for the next phase.

## 7. Migration Runner: CSV Download

This phase focused on implementing the core logic for the migration: downloading the lead data as a CSV file. This was an iterative process.

1.  **Initial Implementation**: Replaced the `migration_runner.py` stub with a full Playwright script designed to log in, navigate to a folder, and trigger a download. The `app.py` endpoint was also updated to return detailed success/error messages from the runner.

2.  **Folder Click Failure (Selector Ambiguity)**: The initial tests failed with a timeout error.
    - **Diagnosis**: The script was looking for an element by its text content (e.g., "Lilly Cooney1"), but the page contained multiple elements with the same text. Playwright couldn't reliably pick the correct one in the folder list.
    - **Solution**: The script was refined to replicate the successful logic from the `folder_scraper`. It now first isolates the "MY FOLDERS" container element and *then* searches for the specific folder link *only within that container*, eliminating the ambiguity.

3.  **Missing "Select All" Step**: After fixing the folder click, the script ran "successfully" but downloaded an empty CSV.
    - **Diagnosis**: The user correctly identified a missing step in the UI flow: all leads must be selected via a checkbox *before* the export can be triggered.
    - **Solution**: A new step was added to the script to click the "Select All" checkbox (`#vxtb-button-check`) after navigating to the folder and before clicking "More" -> "Export".

4.  **Download Path Clarification**: The user noted the downloaded file was not in the system's "Downloads" folder.
    - **Confirmation**: Confirmed that the script is designed to save downloaded files to a project-specific directory: `backend/cache/downloads/`. This keeps all project artifacts self-contained.

### Current Status (CSV Download)
- The `run_migration` function can now reliably log in, navigate to a specific folder, select all leads, and download the corresponding CSV file.
- The downloaded file is correctly saved to `backend/cache/downloads/`.
- The application is ready for the next step: parsing the CSV data.

## 8. New Strategy: Bulk CSV Import

To improve migration speed and reliability, the project's strategy was pivoted away from single-lead UI automation to a more robust bulk CSV import method for Boldtrail.

### 8.1. CSV Transformation

The core of this new approach is the `transform_vortex_to_boldtrail_csv` function, which was developed through an iterative process.

1.  **Initial Transformation Logic**: The previous one-by-one lead creation function was entirely replaced with logic to transform the downloaded Vortex CSV into a new CSV matching Boldtrail's required format. The initial script successfully created the file with the correct headers.

2.  **Data Mapping & Cleaning (Debugging)**: A user review of the first generated CSV revealed several data mapping issues.
    - **Diagnosis**: The `first_name`, `last_name`, address, and `cell_phone_1` columns were blank. This was due to incorrect source column names and a need for more robust data handling.
    - **Solution**: The transformation script was significantly improved to:
        - Correctly split the `Name` field into `first_name` and `last_name`.
        - Map `Property Address`, `Property City`, `Property State`, and `Property Zip` from the Vortex file to their corresponding Boldtrail fields.
        - Intelligently find the first available phone number from a list of possible source columns (`Phone`, `Phone 1`, `Phone 2`).
        - Clean the extracted phone number to be purely numeric.

### Current Status (Transformation Complete)
- The application can now successfully download a CSV from Vortex and transform it into a new, correctly formatted `boldtrail_upload.csv`.
- All data, including names, addresses, and phone numbers, is now accurately mapped and cleaned.
- The application is ready for the final implementation step: automating the login and upload of this new CSV to Boldtrail's bulk import page.

### 8.2. Boldtrail Upload Automation

The final piece of the project was to automate the multi-step upload wizard in Boldtrail. This was a highly iterative process requiring precise selectors and handling of modern web UI behaviors.

1.  **Navigation and Responsive UI**: The initial script struggled to find the "Lead Engine" button.
    - **Diagnosis**: The button was hidden behind a "More" menu on smaller browser window sizes.
    - **Solution**: The script was updated to launch the Playwright browser in a maximized state (`--start-maximized`). This ensured the UI rendered in its full desktop view, making all menu items directly accessible and the script more reliable.

2.  **Selector Debugging**: Several selectors failed during development.
    - **Login**: The login was made robust by using keyboard navigation (`Tab` and `Enter`) and by waiting for a specific dashboard element to appear before proceeding. Several regressions on this logic were caught and fixed by the user.
    - **Lead Engine Button**: The initial selectors were too brittle. The final, successful selector targets the button's container `div` based on the exact text it contains: `div:has-text('LeadEngine')`.
    - **"I Understand" Checkbox**: The initial generic selector `input[type='checkbox']` failed because it matched multiple elements. This was resolved by using the more specific `input.base-input` selector provided by the user.

3.  **Final Wizard Flow**: The script was incrementally built to handle each page of the upload wizard:
    - Navigates to "Lead Engine".
    - Clicks "Start an Import", then "Get Started".
    - Selects the generated `boldtrail_upload.csv` file, correctly handling the hidden file input element.
    - Checks the "I understand" terms and conditions box.
    - Clicks "Next".
    - Clicks "Next" again on the lead routing page.
    - Adds the `vortexsync` tag to the import.
    - Clicks the final "Finish" button to start the import.

## Final Project Status: Complete

- The end-to-end migration process is fully automated.
- The application successfully scrapes folders from Vortex.
- It downloads leads from a selected folder, transforms the data into a Boldtrail-compatible format, and saves it to a new CSV.
- It then logs into Boldtrail and navigates the entire bulk import wizard, uploading the generated CSV and applying the correct tag.
- The project is complete and meets all requirements outlined in the initial build guide and PRD. 
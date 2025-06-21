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

## 9. Refactoring for Reusability

To accommodate the new "Expireds" migration feature without duplicating code, a significant refactoring was undertaken.
- **Shared Logic Identified**: The CSV transformation and Boldtrail upload functions were nearly identical for both the folder-based migration and the planned expireds migration.
- **Utility Module Created**: A new file, `backend/playwright/boldtrail_utils.py`, was created.
- **Functions Moved**: The `transform_vortex_to_boldtrail_csv` and `upload_csv_to_boldtrail` functions were moved from `migration_runner.py` into `boldtrail_utils.py`. The `folder_name` parameter was generalized to `source_name` to handle both folders and filters.
- **Scripts Updated**: Both `migration_runner.py` and the new `expired_scraper.py` were updated to import and use these shared functions, resulting in a cleaner, more maintainable codebase.

## 10. New Feature: Expireds Migration

A major new feature was added to allow for a one-click migration of leads from a predefined filter.
- **Frontend Button**: A new "Migrate Latest Expireds (Bristol County, MA)" button was added to the UI in `frontend/src/app/page.tsx`.
- **API Endpoint**: A new API route, `/api/migrate-expireds`, was created in `backend/app.py`.
- **New Scraper Script**: A new Playwright script, `backend/playwright/expired_scraper.py`, was created to:
    1. Log into Vortex.
    2. Click the "Daily Expireds" filter in the sidebar.
    3. Follow the same "Select All" -> "More" -> "Export" flow to download the CSV.
    4. Call the shared utility functions from `boldtrail_utils.py` to transform the CSV and upload it to Boldtrail.

## 11. Agent Notes Enhancement

Based on user feedback, the format of the `agent_notes` field in the final Boldtrail upload was significantly improved.
- **Previous Format**: A short, static paragraph summarizing a few key fields.
- **New Format**: A dynamic, comprehensive, and clean-looking list. The new `transform_vortex_to_boldtrail_csv` function now iterates through *all* columns of the source Vortex CSV. For any column with a non-empty value, it generates a bullet-pointed line (e.g., `* roof type: asphalt`) in the note.
- **Universal Application**: Because this logic is in the shared `boldtrail_utils.py` file, this enhancement applies to both folder-based and expireds-based migrations automatically.

## 12. Debugging and Finalization

The final phase involved iterative debugging and hardening of the automation scripts to ensure reliability.
- **Login Unification**: Fixed a login failure in the new expireds scraper by standardizing the login method across all scripts (`migration_runner.py`, `expired_scraper.py`) to use the more robust keyboard-based navigation (`Tab`, `Tab`, `Enter`).
- **Browser Maximization**: Ensured all Playwright instances launch with a maximized browser window (`--start-maximized` and `no_viewport=True`) to prevent responsive UI elements from hiding and causing selector failures.
- **Folder Selection Logic**: Resolved a critical timeout in the folder migration script. The fix involved aligning the `migration_runner.py`'s folder-finding logic to perfectly match the `folder_scraper.py`'s logic, first by locating the "MY FOLDERS" `span` and then finding the specific folder `div` within that container. An explicit `scroll_into_view_if_needed()` call was also added to handle long folder lists.
- **Strategic Pauses**: Added brief, 1-second `wait_for_timeout` calls after critical UI interactions (like clicking a folder and selecting all leads) to give the web application's UI time to react and update, increasing script stability.

## 13. Project Archival

The project was finalized by preparing it for version control.
- **`.gitignore` Created**: A comprehensive `.gitignore` file was added to the project root to exclude credentials, virtual environments, cache files, and OS-specific files.
- **`.env.example` Created**: An example environment file was created to serve as a template for future users.
- **`README.md` Created**: A detailed README was written, providing a project overview, feature list, and step-by-step setup and run instructions.
- **GitHub Commit**: The entire project was successfully committed to a new GitHub repository, marking the completion of the development cycle. 

## 14. Real-time Progress View

To provide a better user experience, the final feature implemented was a real-time progress log that mimics a CLI interface. This required a significant refactoring of the backend-frontend communication.

- **Backend Refactoring (Generators & Streaming)**:
    - All core Playwright functions (`run_migration`, `run_expired_migration`, and the utilities in `boldtrail_utils.py`) were converted from standard functions into **generator functions**. Instead of `print()`ing their status, they now `yield` each log message as it occurs.
    - A new `stream_wrapper` decorator was created in `app.py` to handle these generators. It wraps the generator's output in a streaming `Response` using the **Server-Sent Events (SSE)** protocol (`mimetype='text/event-stream'`).
    - The API endpoints (`/api/run-migration`, `/api/migrate-expireds`) were updated to use this streaming response mechanism.

- **Frontend Implementation (CLI Display & EventSource)**:
    - The main UI in `frontend/src/app/page.tsx` was overhauled to include a new state, `isMigrating`, which conditionally renders a "CLI" display.
    - This display is a styled `div` with a dark background and monospaced, green/yellow text, which automatically scrolls to the bottom as new messages arrive.
    - A `startStream` function was created that uses the browser's `fetch` API to make a `POST` request to the backend. It then reads the resulting response body as a stream.
    - As data chunks arrive, they are decoded, parsed as Server-Sent Events, and appended to a `logMessages` state array, causing the CLI display to update in real-time.
    - When the backend sends a special `__DONE__` message, the stream is closed, and the user is presented with a button to close the log and return to the main view.

- **Final Commit**: All changes for the real-time logging feature were committed and pushed to the GitHub repository, completing the project's feature set.

## 15. Deployment Troubleshooting

The deployment process to Fly.io encountered an issue where the `fly` CLI command, after initially working, suddenly became unrecognized by PowerShell (`The term 'fly' is not recognized...`).

- **Diagnosis**: This was identified as a `PATH` environment variable issue. The installer had updated the system's PATH, but the change had not been picked up by the active terminal session. Restarting the terminal did not resolve the issue immediately.
- **Solution**: The problem was bypassed by using the full, absolute path to the executable (`C:\Users\antar\.fly\bin\flyctl.exe`) for all subsequent CLI calls. This ensures the command is found regardless of the shell's current `PATH` configuration.

## 16. Deployment and Troubleshooting on Fly.io

The deployment process involved a lengthy and iterative debugging cycle to resolve several issues that only appeared in the production environment.

1.  **Initial `ModuleNotFoundError`**: The first deployment failed because the Python script couldn't find the `backend` module.
    -   **Incorrect Fix #1**: `ENV PYTHONPATH=/app` and `python -m` were added to the Dockerfile. This did not work as it created a different path context issue.
    -   **Incorrect Fix #2**: A `sys.path.append()` call was added to the script. This also failed to resolve the issue.
    -   **Correct Fix**: The root cause was identified as an unused `from backend.utils.logger import log` statement in both `expired_scraper.py` and its dependency, `boldtrail_utils.py`. Removing this legacy import resolved the module loading crash.

2.  **Fly.io App Suspension**: The application was being suspended after 10 failed health checks.
    -   **Diagnosis**: The `fly.toml` was configured with an `[http_service]`, causing Fly.io to treat the script as a web server and ping it. Since the script does not listen on a port, the health checks failed.
    -   **Correct Fix**: The `[http_service]` and `[[vm]]` sections were removed from `fly.toml`, correctly defining the application as a simple, non-web task.

3.  **SMTP Authentication Failure**: The switch to Gmail for email reporting initially failed.
    -   **Diagnosis**: The initial error with Outlook was due to Microsoft disabling Basic Authentication. After switching to Gmail, a `KeyError: 'SMTP_USER'` appeared in the logs.
    -   **Correct Fix**: A single line in `email_reporter.py` was still referencing the old `os.environ["SMTP_USER"]` variable instead of the new `EMAIL_USER`. Correcting this line fixed the authentication logic.

4.  **Playwright Headless Mode Crash**: After fixing the code issues, the Playwright browser began crashing inside the container.
    -   **Diagnosis**: Logs showed the script was trying to launch a "headed" browser in a headless Linux environment. Several attempts to fix this by conditionally setting `headless=True` or defining a `viewport` were unsuccessful due to conflicting arguments.
    -   **Correct Fix**: The final solution was to remove all conditional logic and conflicting arguments (`no_viewport=True`) and simply force `headless=True` while setting a large, fixed viewport size (`{'width': 1920, 'height': 1080}`).

5.  **Build Cache Issue**: The final logic bug (incorrectly reporting success as failure) was not being reflected in the deployment.
    -   **Diagnosis**: The Fly.io build process was likely using a cached Docker layer that contained the old, buggy version of the script.
    -   **Correct Fix**: The final deployment was run with the `--no-cache` flag to force a complete rebuild, ensuring the latest version of all files was used.

After resolving all of these issues, the application was deployed successfully, the migration ran, and a correct success email was sent. 

## 17. Email Reporting Enhancement

The email reporting system was improved to provide more detailed information about the migration process.

1. **Enhanced Email Content**:
    - Added lead count to the email body
    - Added a list of all lead names that were attempted to be migrated
    - Improved error reporting to include more context about failures
    - Maintained consistent email format regardless of success/failure

2. **Implementation Details**:
    - Modified the email template to always include lead count and names
    - Ensured lead names are captured even when the migration fails
    - Added more detailed error messages in the email body
    - Improved logging to capture all relevant information for the email report

## 18. Fly.io Deployment and Testing

The application was deployed to Fly.io for production use, with several iterations of testing and improvements.

1. **Initial Deployment**:
    - Successfully deployed the application to Fly.io
    - Set up the necessary environment variables and secrets
    - Configured the deployment to run the migration script

2. **Testing and Observations**:
    - Ran multiple test migrations to verify functionality
    - Observed intermittent success/failure patterns
    - Identified various timeout issues at different stages of the migration
    - Documented successful and failed migration attempts with detailed logs

3. **Current Status**:
    - The application is deployed and functional on Fly.io
    - Email reporting is working with improved detail
    - Migration process is operational but showing some reliability issues
    - Further improvements to reliability are being investigated 

## Migration Script Retry Logic Implementation (2024-03-19)
- Added robust retry mechanism to the daily migration script
- Implemented automatic retries for failed migrations:
  - Maximum of 10 retries per day
  - 3-minute delay between retry attempts
  - Clear attempt counting in logs and email notifications
- Enhanced email reporting:
  - Success emails include lead count and names
  - Failure emails show attempt number (e.g., "Attempt 2/10")
  - Added retry information to failure notifications
- Improved error handling:
  - Separate handling for migration failures vs email sending failures
  - Retry on email sending failures if migration was successful
  - Clear logging of retry attempts and delays
- Script behavior:
  - Runs daily at 8:30 AM UTC
  - Stops after successful migration until next day
  - Automatically retries on failures with 3-minute intervals
  - Stops after max retries reached for the day 
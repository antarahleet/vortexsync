# Vortex → Boldtrail Lead Migration Automation PRD

## 1. Background & Problem Statement
Agents currently export seller‐lead folders from **Vortex** and manually enter them into **Boldtrail** CRM. This is slow, error‑prone, and distracts from revenue‑generating activity.

## 2. Goal & Objectives
* **Automate** migration of leads from any selected Vortex folder to Boldtrail.  
* Provide a **self‑service web interface** for agents to trigger the process without coding.  
* Generate a rich, descriptive **lead note** in Boldtrail that *includes the origin folder name* plus property/tax data.

## 3. Success Metrics
| Metric | Target |
| --- | --- |
| Lead creation accuracy | 100 % of selected leads have correct field values |
| Avg. migration time | < 5 s per lead |
| Error rate | < 1 % (failed leads / total) |
| User satisfaction | > 8 / 10 in internal survey |

## 4. User Personas
1. **Real‑Estate Agent (Primary User)** – runs migrations, reviews logs.
2. **Team Admin / Developer** – configures credentials, monitors uptime & errors.

## 5. User Stories
* **US‑01**: As an agent, I can **refresh** the list of Vortex folders so I always see the latest folders.  
* **US‑02**: As an agent, I can **select a folder** from a searchable dropdown.  
* **US‑03**: As an agent, I can **preview** the number of leads before running migration.  
* **US‑04**: As an agent, I can **start migration** for a specific folder and see its real-time progress.  
* **US‑05**: As an agent, I can trigger a **separate migration for all recent "Daily Expireds"** with a single click.  
* **US‑06**: As an agent, I can see a **complete, real-time log** in the UI as the migration runs.  

## 6. Functional Requirements
### 6.1 Folder Retrieval
* **FR‑1**: System logs into Vortex with stored credentials from an `.env` file.  
* **FR‑2**: Scrape all **parent folders** (+ subfolders if present) from the sidebar.  
* **FR‑3**: Cache folder list in JSON or DB.  
* **FR‑4**: Expose `GET /api/folders` (returns cached list) and `POST /api/update-folders` (refreshes cache).

### 6.2 Lead Migration (Bulk CSV Method)
* **FR‑5**: Given a folder name OR a predefined filter (e.g., "Daily Expireds"), navigate to the corresponding page in Vortex.
* **FR‑6**: Programmatically select all leads and trigger the "Export" function to download a CSV of the lead data.
* **FR‑7**: Save the downloaded CSV to a local cache directory.
* **FR‑8**: Transform the Vortex CSV into a new, Boldtrail-compatible CSV. This includes:
    * Splitting the `Name` field into `first_name` and `last_name`.
    * Finding the first available phone number and cleaning it to be purely numeric.
    * Mapping all relevant address fields.
    * **Generating a comprehensive, bulleted list of all non-empty fields from the source CSV to be used as the `agent_notes` in Boldtrail.** The source folder/filter is included at the top of this note.
* **FR‑9**: Log into Boldtrail using stored credentials.
* **FR‑10**: Navigate to the "Lead Engine" -> "Bulk Import" tool.
* **FR‑11**: Automate the multi-step import wizard to upload the transformed CSV, accept terms, and apply a `vortexsync` tag to the import.

### 6.3 Web UI
* **FR‑12**: No user login required for the local tool.
* **FR‑13**: Main page displays a dropdown populated via `/api/folders`.
* **FR‑14**: "Update Vortex Folders" button triggers `/api/update-folders` and provides interactive progress/success feedback.
* **FR‑15**: "Start Migration" button posts to `/api/run-migration` with the selected folder.
* **FR‑16**: A separate "Migrate Latest Expireds" button posts to `/api/migrate-expireds`.
* **FR‑17**: The UI displays a live, streaming log of real-time status messages from the backend for all migration operations.

## 7. Non‑Functional Requirements
| Category | Requirement |
| --- | --- |
| **Performance** | End‑to‑end runtime ≤ 10 min for 500 leads |
| **Scalability** | Handle 1,000 leads/run without code changes |
| **Availability** | 99 % uptime for API & UI |
| **Security** | Credentials in env vars; TLS enforced; no CSV persisted after run |
| **Logging** | JSON log per run; errors emailed/slacked to admin |
| **Maintainability** | Modular codebase with automated tests |
| **Cache**: Local JSON files in `/backend/cache/`.

## 8. Technical Architecture
```
[Frontend (Next.js + ShadCN)]
        │  fetch /api/*
[Python API (Flask/FastAPI)] ──▶ [Playwright Worker]
        │                         │
        │                         └──▶ Headless Chromium
        │                                   │
   [Supabase / JSON] ◀── Cache & Logs ──────┘
```
* **Hosting**: Fly.io / Render (Docker)  
* **Browser**: Headless Chromium via Playwright  
* **Cache**: Local JSON (phase 1) → Supabase (phase 2)

## 9. Constraints & Assumptions
* Vortex DOM remains stable (no major redesign).  
* Boldtrail's bulk import wizard flow remains stable.  
* CSV format from Vortex contains all necessary lead data.  
* English locale only.

## 10. Out‑of‑Scope (Phase 1)
* Lead deduplication in Boldtrail.  
* Background scheduling (cron) – manual trigger only.  
* Multi‑agent credential storage.  
* Smart‑campaign assignment.

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
* **US‑04**: As an agent, I can **start migration** and watch real‑time progress and error logs.  
* **US‑05**: As an agent, I receive a **summary report** when the migration finishes.  

## 6. Functional Requirements
### 6.1 Folder Retrieval
* **FR‑1**: System logs into Vortex with stored credentials.  
* **FR‑2**: Scrape all **parent folders** (+ subfolders if present) from the sidebar.  
* **FR‑3**: Cache folder list in JSON or DB.  
* **FR‑4**: Expose `GET /api/folders` (returns cached list) and `POST /api/update-folders` (refreshes cache).

### 6.2 Lead Migration
* **FR‑5**: Given a folder name, navigate to that folder and click **Download CSV**.  
* **FR‑6**: Save CSV to `/tmp`, parse each row.  
* **FR‑7**: For every lead row:
  * Extract names, phones, emails, address, property & tax details.  
  * Generate a descriptive paragraph **including the folder name**.  
  * Log into Boldtrail, click **Add Contact**.  
  * Populate fields:
    * *First/Last Name* – first contact on record  
    * *Email / Phone(s)* – primary + secondary  
    * *Address* – street, city, state, zip  
    * *Contact permissions* – enable call, text, email  
    * *Lead Type* – Seller  
    * *Lead Status* – New Lead  
    * *Lead Source* – VORTEX  
    * *Note* – generated paragraph with folder name  
  * Submit form.
* **FR‑8**: Record success/failure per lead in run log.

### 6.3 Web UI
* **FR‑9**: Secure login (basic auth or Supabase magic link).  
* **FR‑10**: Dropdown populated via `/api/folders` with search filter.  
* **FR‑11**: "Update Vortex Folders" button triggers `/api/update-folders`.  
* **FR‑12**: "Start Migration" button posts to `/api/run-migration` with selected folder.  
* **FR‑13**: Display real‑time logs and final summary.

## 7. Non‑Functional Requirements
| Category | Requirement |
| --- | --- |
| **Performance** | End‑to‑end runtime ≤ 10 min for 500 leads |
| **Scalability** | Handle 1,000 leads/run without code changes |
| **Availability** | 99 % uptime for API & UI |
| **Security** | Credentials in env vars; TLS enforced; no CSV persisted after run |
| **Logging** | JSON log per run; errors emailed/slacked to admin |
| **Maintainability** | Modular codebase with automated tests |

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
* Boldtrail *Add Contact* has no CAPTCHA and loads < 5 s.  
* CSV contains all necessary lead data.  
* English locale only.

## 10. Out‑of‑Scope (Phase 1)
* Lead deduplication in Boldtrail.  
* Background scheduling (cron) – manual trigger only.  
* Multi‑agent credential storage.  
* Smart‑campaign assignment.

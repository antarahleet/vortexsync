# Step‑by‑Step Build Guide for **Vortex → Boldtrail Lead Migration**

> **Use this guide *exactly in order*.** Each step produces files the next step relies on.  
> Root project folder will be called **`vortexsync`**.

---

## 0. Prerequisites

```bash
# At repo root
python -m venv .venv
source .venv/bin/activate
pip install playwright flask pandas python-dotenv
playwright install chromium
npm create next-app@latest frontend --ts --eslint --src-dir --app --import-alias "@/*"
```

Add **`.env`** (repo root):

```
VORTEX_USER=you@example.com
VORTEX_PASS=•••
BOLDTRAIL_USER=you@example.com
BOLDTRAIL_PASS=•••
```
STOP HERE AND TELL USER THAT YOU HAVE FINISHED THIS STEP AND AWAIT INSTRUCTIONS.
---

## 1. File‑tree Skeleton

```
vortexsync/
├─ backend/
│  ├─ app.py
│  ├─ cache/               # JSON folder cache + run logs
│  ├─ playwright/
│  │   ├─ folder_scraper.py
│  │   └─ migration_runner.py
│  └─ utils/
│      └─ logger.py
├─ frontend/               # created by create‑next‑app
└─ requirements.txt
```

Add **`backend/__init__.py`** (empty) so Python treats folder as a package.

STOP HERE AND TELL USER THAT YOU HAVE FINISHED THIS STEP AND AWAIT INSTRUCTIONS.
---

## 2. `backend/utils/logger.py`

```python
import json, datetime, pathlib
LOG_DIR = pathlib.Path(__file__).resolve().parent.parent / "cache"
LOG_DIR.mkdir(exist_ok=True)

def log(event: str, data: dict):
    ts = datetime.datetime.utcnow().isoformat()
    entry = {"ts": ts, "event": event, **data}
    fp = LOG_DIR / f"{ts[:10]}.log.jsonl"
    with fp.open("a") as f:
        f.write(json.dumps(entry) + "\n")
```
STOP HERE AND TELL USER THAT YOU HAVE FINISHED THIS STEP AND AWAIT INSTRUCTIONS.
---

## 3. `backend/playwright/folder_scraper.py`

```python
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv; load_dotenv()
import os, json, pathlib
from backend.utils.logger import log

CACHE = pathlib.Path(__file__).resolve().parent.parent / "cache/folders.json"

def scrape_folders():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto("https://login.vortex.com")
        page.fill("#email", os.getenv("VORTEX_USER"))
        page.fill("#password", os.getenv("VORTEX_PASS"))
        page.click("text=Login")
        page.wait_for_selector("text=Folders")
        folder_elements = page.query_selector_all("css=div.folder-list a")
        folders = [el.inner_text().strip() for el in folder_elements]
        CACHE.write_text(json.dumps(sorted(set(folders)), indent=2))
        log("folders_updated", {"count": len(folders)})
        ctx.close(); browser.close()
        return folders
```

*Replace `css=div.folder-list a` with actual selector after inspection.*

STOP HERE AND TELL USER THAT YOU HAVE FINISHED THIS STEP AND AWAIT INSTRUCTIONS.
---

## 4. `backend/playwright/migration_runner.py`

*Stub now; will be completed after folder list works.*

```python
def run_migration(folder_name: str):
    # 1. login, click folder, download CSV
    # 2. parse CSV w/ pandas
    # 3. iterate rows, open Boldtrail, add contact
    pass
```
STOP HERE AND TELL USER THAT YOU HAVE FINISHED THIS STEP AND AWAIT INSTRUCTIONS.
---

## 5. `backend/app.py`

```python
from flask import Flask, jsonify, request
from backend.playwright.folder_scraper import scrape_folders
from backend.playwright.migration_runner import run_migration
import json, pathlib

app = Flask(__name__)
CACHE = pathlib.Path(__file__).resolve().parent / "cache/folders.json"

@app.route("/api/folders", methods=["GET"])
def get_folders():
    if CACHE.exists():
        return jsonify(json.load(CACHE.open()))
    return jsonify([])

@app.route("/api/update-folders", methods=["POST"])
def update_folders():
    folders = scrape_folders()
    return jsonify({"updated": len(folders)})

@app.route("/api/run-migration", methods=["POST"])
def run_migration_endpoint():
    folder = request.json["folder"]
    run_migration(folder)
    return jsonify({"status": "started"})
```

Run backend:

```bash
python -m flask --app backend.app run --port 5000 --debug
```
STOP HERE AND TELL USER THAT YOU HAVE FINISHED THIS STEP AND AWAIT INSTRUCTIONS.
---

## 6. Frontend Setup (`frontend/`)

1. **Create proxy** in `frontend/.env.local`  
   ```
   NEXT_PUBLIC_API=http://localhost:5000
   ```

2. **Folder Fetcher util** `frontend/src/lib/api.ts`:

```ts
export async function getFolders(){
  const res = await fetch(process.env.NEXT_PUBLIC_API + "/api/folders");
  return res.json();
}
export async function updateFolders(){
  return fetch(process.env.NEXT_PUBLIC_API + "/api/update-folders", {method:"POST"});
}
export async function runMigration(folder:string){
  return fetch(process.env.NEXT_PUBLIC_API + "/api/run-migration",{
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({folder})
  });
}
```

3. **Index Page** (`frontend/src/app/page.tsx`) shows:
   * Dropdown (Radix + ShadCN) populated by `getFolders()`
   * “Update Vortex Folders” triggers `updateFolders()` then reloads dropdown
   * “Start Migration” calls `runMigration(selected)` and displays toast

STOP HERE AND TELL USER THAT YOU HAVE FINISHED THIS STEP AND AWAIT INSTRUCTIONS.
---

## 7. Complete `migration_runner.py`

*After folder dropdown works, expand stub:*

1. Use Playwright to click folder link (`page.click(f"text={folder_name}")`).
2. Wait for Download CSV button; capture download to `/tmp/lead.csv`.
3. `pandas.read_csv` → generate note paragraph:  

```python
note = f"[Folder: {folder}]\n{primary_name} lives with {secondary}..."
```

4. Log into Boldtrail:  
   * Click **New Lead** (`#newLeadBtn`)  
   * Fill form fields  
   * Paste note paragraph  
   * Submit & `log("lead_created", {...})`
   
STOP HERE AND TELL USER THAT YOU HAVE FINISHED THIS STEP AND AWAIT INSTRUCTIONS.
---

## 8. Dockerisation (optional)

`Dockerfile` at repo root:

```Dockerfile
FROM python:3.11
WORKDIR /app
COPY ./backend /app/backend
COPY requirements.txt .
RUN pip install -r requirements.txt && playwright install chromium
ENV PYTHONPATH=/app
CMD ["python", "-m", "flask", "--app", "backend.app", "run", "--host", "0.0.0.0"]
```

Expose `5000`.

---

## 9. Run End‑to‑End (local)

```bash
# Terminal 1
source .venv/bin/activate
python -m flask --app backend.app run

# Terminal 2
cd frontend
npm run dev
```

Open `http://localhost:3000`.

---

> **NEXT STEPS**  
> *Fill in selectors in `migration_runner.py` and add robust error handling.*  
> Use real credentials in `.env`.  Confirm folder list is accurate, then build Boldtrail automation logic step by step.

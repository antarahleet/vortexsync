from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import pathlib
import os

# Load .env file from the project root
project_root = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=project_root / ".env")

from backend.playwright.folder_scraper import scrape_folders
from backend.playwright.migration_runner import run_migration
from backend.playwright.expired_scraper import run_expired_migration
import json

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

CACHE = pathlib.Path(__file__).resolve().parent / "cache/folders.json"

@app.route("/api/folders", methods=["GET"])
def get_folders():
    if CACHE.exists():
        return jsonify(json.load(CACHE.open()))
    return jsonify([])

@app.route("/api/update-folders", methods=["POST"])
def update_folders():
    try:
        folders = scrape_folders()
        return jsonify({"status": "success", "updated": len(folders)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/run-migration", methods=["POST"])
def run_migration_endpoint():
    folder = request.json.get("folder")
    if not folder:
        return jsonify({"status": "error", "message": "Folder not specified."}), 400
    
    result = run_migration(folder)
    status_code = 200 if result.get("status") == "success" else 500
    return jsonify(result), status_code

@app.route("/api/migrate-expireds", methods=["POST"])
def migrate_expireds_endpoint():
    result = run_expired_migration()
    status_code = 200 if result.get("status") == "success" else 500
    return jsonify(result), status_code 
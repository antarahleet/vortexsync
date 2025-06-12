from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from dotenv import load_dotenv
import pathlib
import os
import time

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

def stream_wrapper(generator_function):
    """Wraps a generator function to stream its yielded output."""
    def streamer(**kwargs):
        def generate():
            for message in generator_function(**kwargs):
                # Format as Server-Sent Event
                yield f"data: {message}\\n\\n"
                time.sleep(0.1) # Small delay to ensure messages are sent separately
            yield "data: __DONE__\\n\\n" # Signal completion
        return Response(generate(), mimetype='text/event-stream')
    return streamer

@app.route("/api/run-migration", methods=["POST"])
def run_migration_endpoint():
    folder = request.json.get("folder")
    if not folder:
        return jsonify({"status": "error", "message": "Folder not specified."}), 400
    
    # Wrap the generator function for streaming
    return stream_wrapper(run_migration)(folder_name=folder)

@app.route("/api/migrate-expireds", methods=["POST"])
def migrate_expireds_endpoint():
    # Wrap the generator function for streaming
    return stream_wrapper(run_expired_migration)() 
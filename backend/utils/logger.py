import json, datetime, pathlib
LOG_DIR = pathlib.Path(__file__).resolve().parent.parent / "cache"
LOG_DIR.mkdir(exist_ok=True)

def log(event: str, data: dict):
    ts = datetime.datetime.utcnow().isoformat()
    entry = {"ts": ts, "event": event, **data}
    fp = LOG_DIR / f"{ts[:10]}.log.jsonl"
    with fp.open("a") as f:
        f.write(json.dumps(entry) + "\n") 
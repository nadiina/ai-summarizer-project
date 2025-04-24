from datetime import datetime


def make_log_entry(file_name: str, payload: dict) -> dict:
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "file_name": file_name,
    }
    entry.update(payload)
    return entry

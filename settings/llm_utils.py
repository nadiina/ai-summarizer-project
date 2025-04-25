from datetime import datetime
from zoneinfo import ZoneInfo


def make_log_entry(file_name: str, payload: dict) -> dict:
    entry = {
        "timestamp": datetime.now(ZoneInfo("Europe/Kyiv")).isoformat(),
        "file_name": file_name,
    }
    entry.update(payload)
    return entry

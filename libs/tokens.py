import os
import time
import json
from datetime import datetime
from libs.logger import log_info

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_FILE = os.path.join(BASE_DIR, "logs", "token_usage.jsonl")
SUMMARY_FILE = os.path.join(BASE_DIR, "logs", "token_total.json")


class TokenTracker:
    def __init__(self, model_name: str = "unknown", prompt: str = ""):
        self.model_name = model_name
        self.prompt = prompt.strip()[:200]
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.start_time = time.time()

    def add_prompt_tokens(self, count: int):
        self.prompt_tokens += count

    def add_completion_tokens(self, count: int):
        self.completion_tokens += count

    def get_total_tokens(self):
        return self.prompt_tokens + self.completion_tokens

    def get_elapsed_time(self):
        return round(time.time() - self.start_time, 3)

    def write_report(self):
        os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)

        now_iso = datetime.now().astimezone().isoformat()

        report_entry = {
            "timestamp": now_iso,
            "model": self.model_name,
            "prompt": self.prompt,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.get_total_tokens(),
            "elapsed_seconds": self.get_elapsed_time()
        }

        with open(REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(report_entry, ensure_ascii=False) + "\n")

        log_info(f"Token usage записано у {REPORT_FILE}")

        total_tokens = self.get_total_tokens()
        summary = {"total_tokens": 0, "last_used": now_iso}

        if os.path.exists(SUMMARY_FILE):
            with open(SUMMARY_FILE, "r", encoding="utf-8") as sf:
                try:
                    summary = json.load(sf)
                except json.JSONDecodeError:
                    pass

        summary["total_tokens"] = summary.get("total_tokens", 0) + total_tokens
        summary["last_used"] = now_iso

        with open(SUMMARY_FILE, "w", encoding="utf-8") as sf:
            json.dump(summary, sf, ensure_ascii=False, indent=2)

        log_info(f"Сумарна статистика оновлена: {summary['total_tokens']} токенів, останнє використання: {summary['last_used']}")

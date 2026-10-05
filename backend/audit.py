"""Small, append-preserving audit log for agent and database-tool activity."""

import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path


AUDIT_PATH = Path(__file__).resolve().parents[1] / "output" / "audit_trail.json"
_LOCK = threading.Lock()
_SECRET_WORDS = ("password", "hash", "api_key", "token", "secret", "credential", "env")


def _short(value, limit: int = 240):
    if isinstance(value, dict):
        return {str(key): _short(item, 100) for key, item in list(value.items())[:8] if not any(word in str(key).lower() for word in _SECRET_WORDS)}
    if isinstance(value, (list, tuple)):
        return [_short(item, 80) for item in list(value)[:6]]
    text = str(value)
    if any(word in text.lower() for word in _SECRET_WORDS):
        return "[redacted]"
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[email redacted]", text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def record_activity(tool_name: str, arguments, result, stop_reason: str) -> None:
    """Append one concise record while preserving all previous records."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        try:
            records = json.loads(AUDIT_PATH.read_text(encoding="utf-8")) if AUDIT_PATH.exists() else []
            if not isinstance(records, list):
                records = []
        except (OSError, json.JSONDecodeError):
            records = []
        records.append({
            "time": datetime.now(timezone.utc).isoformat(),
            "tool_name": tool_name,
            "arguments": _short(arguments),
            "result": _short(result),
            "stop_reason": stop_reason,
        })
        AUDIT_PATH.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BROKER_HOST = "localhost"
BROKER_PORT = 1883
MQTT_TOPIC = "traffic/auckland/corridor"
PUBLISH_SOURCE_CSV = PROJECT_ROOT / "data_processed" / "travel_time" / "travel_time_10min.csv"
STATUS_DIR = PROJECT_ROOT / "iot_db" / "mqtt" / "status"
STATUS_FILES = {
    "publisher": STATUS_DIR / "publisher_status.json",
    "subscriber": STATUS_DIR / "subscriber_status.json",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        try:
            return value.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def status_file_path(component: str) -> Path:
    if component not in STATUS_FILES:
        raise ValueError(f"Unknown MQTT component: {component}")
    return STATUS_FILES[component]


def default_status(component: str) -> dict[str, Any]:
    return {
        "component": component,
        "state": "not_started",
        "updated_at": None,
        "message_count": 0,
        "broker_host": BROKER_HOST,
        "broker_port": BROKER_PORT,
        "topic": MQTT_TOPIC,
        "last_message_time": None,
        "last_payload": None,
        "last_error": None,
    }


def read_component_status(component: str) -> dict[str, Any]:
    path = status_file_path(component)
    if not path.exists():
        return default_status(component)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        broken_status = default_status(component)
        broken_status["state"] = "unreadable"
        broken_status["last_error"] = f"Could not read {path.name}"
        return broken_status

    status = default_status(component)
    status.update(payload)
    return status


def write_component_status(component: str, state: str, **fields: Any) -> dict[str, Any]:
    path = status_file_path(component)
    path.parent.mkdir(parents=True, exist_ok=True)

    status = read_component_status(component)
    status.update(
        {
            "component": component,
            "state": state,
            "updated_at": _utc_now_iso(),
        }
    )
    status.update({key: _json_safe(value) for key, value in fields.items()})

    payload_text = json.dumps(status, indent=2)

    last_error: Exception | None = None
    for _ in range(5):
        temp_path = path.with_name(f"{path.stem}_{os.getpid()}_{uuid4().hex}.tmp")
        try:
            temp_path.write_text(payload_text, encoding="utf-8")
            temp_path.replace(path)
            return status
        except PermissionError as exc:
            last_error = exc
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass
            time.sleep(0.05)

    if last_error is not None:
        path.write_text(payload_text, encoding="utf-8")
        return status

    return status


def read_all_statuses() -> dict[str, dict[str, Any]]:
    return {component: read_component_status(component) for component in STATUS_FILES}


def clear_all_statuses() -> None:
    for path in STATUS_FILES.values():
        if path.exists():
            path.unlink()

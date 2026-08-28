from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from typing import Any

import yaml


def to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)


def from_json(value: str) -> Any:
    return json.loads(value)


def to_yaml(value: Any) -> str:
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=True).rstrip()


def from_yaml(value: str) -> Any:
    if len(value) > 65_536:
        raise ValueError("YAML filter input exceeds 65536 characters")
    if re.search(r"(^|\s)[&*][A-Za-z0-9_-]+", value):
        raise ValueError("YAML anchors and aliases are not supported in expressions")
    return yaml.safe_load(value)


def number(value: Any) -> int | float:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float):
        return value
    text = str(value).strip()
    return float(text) if any(marker in text.lower() for marker in (".", "e")) else int(text)


def boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return value != 0
    normalized = str(value).strip().lower()
    if normalized in {"true", "yes", "1", "on"}:
        return True
    if normalized in {"false", "no", "0", "off", ""}:
        return False
    raise ValueError(f"cannot convert {value!r} to boolean")


def abbreviate(value: Any, maximum: int) -> str:
    if maximum < 4:
        raise ValueError("abbreviate maximum must be at least 4")
    text = str(value)
    return text if len(text) <= maximum else text[: maximum - 3] + "..."


def split(value: Any, separator: str | None = None) -> list[str]:
    return str(value).split(separator)


def keys(value: Mapping[Any, Any]) -> list[Any]:
    return list(value.keys())


def values(value: Mapping[Any, Any]) -> list[Any]:
    return list(value.values())


def first(value: Sequence[Any]) -> Any:
    return value[0] if value else None


def last(value: Sequence[Any]) -> Any:
    return value[-1] if value else None


def date_format(value: Any, format: str = "yyyy-MM-dd'T'HH:mm:ss") -> str:
    parsed = _datetime(value)
    replacements = {
        "yyyy": f"{parsed.year:04d}",
        "SSSSSS": f"{parsed.microsecond:06d}",
        "SSS": f"{parsed.microsecond // 1000:03d}",
        "MM": f"{parsed.month:02d}",
        "dd": f"{parsed.day:02d}",
        "HH": f"{parsed.hour:02d}",
        "mm": f"{parsed.minute:02d}",
        "ss": f"{parsed.second:02d}",
    }
    return re.sub(
        r"yyyy|SSSSSS|SSS|MM|dd|HH|mm|ss",
        lambda match: replacements[match.group(0)],
        format,
    ).replace("'", "")


def date_add(value: Any, amount: int, unit: str) -> datetime:
    parsed = _datetime(value)
    normalized = unit.upper()
    increments = {
        "WEEKS": timedelta(weeks=amount),
        "DAYS": timedelta(days=amount),
        "HOURS": timedelta(hours=amount),
        "MINUTES": timedelta(minutes=amount),
        "SECONDS": timedelta(seconds=amount),
        "MILLISECONDS": timedelta(milliseconds=amount),
    }
    if normalized not in increments:
        raise ValueError(f"unsupported dateAdd unit {unit!r}")
    return parsed + increments[normalized]


def is_empty(value: Any) -> bool:
    return (
        value is None
        or value == ""
        or (
            isinstance(value, Mapping | Sequence) and not isinstance(value, str) and len(value) == 0
        )
    )


def _datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=UTC)
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)

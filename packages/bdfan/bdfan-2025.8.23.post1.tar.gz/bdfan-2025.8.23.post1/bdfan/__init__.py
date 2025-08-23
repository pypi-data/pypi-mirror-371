import json
from pathlib import Path


_src = Path(__file__).parent


def load() -> list[dict]:
    return json.loads((_src / "bdfan_with_hearts.json").read_text(encoding='utf-8'))


def load_mapping() -> dict[int, dict[int, dict]]:
    # mapping[month][day] = entry
    data = load()
    mapping = {}
    for entry in data:
        month = entry['month']
        day = entry['day']
        mapping.setdefault(month, {})[day] = entry
    return mapping


def load_date(month: int, day: int) -> dict:
    return load_mapping().get(month, {}).get(day, {})


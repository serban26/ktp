from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


_BASE_DIR = Path(__file__).resolve().parent
_KB_DIR = _BASE_DIR / "kb_data"


def _load_module(name: str) -> Dict[str, Any]:
    path = _KB_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


_MODULE_NAMES = [
    "general",
    "engine_ignition",
    "engine_fuel",
    "engine_mechanical",
    "cooling",
    "brakes",
    "wheels",
    "steering_suspension",
    "transmission",
    "climate_ac",
    "electrical_lighting",
]


CAR_SYSTEMS: List[Dict[str, Any]] = []
SYMPTOMS: List[Dict[str, Any]] = []
RULES: List[Dict[str, Any]] = []


_seen_system_ids = set()
_seen_symptom_ids = set()
_seen_rule_ids = set()


for module_name in _MODULE_NAMES:
    data = _load_module(module_name)

    for system in data.get("systems", []):
        system_id = system["id"]
        if system_id not in _seen_system_ids:
            CAR_SYSTEMS.append(system)
            _seen_system_ids.add(system_id)

    for symptom in data.get("symptoms", []):
        symptom_id = symptom["id"]
        if symptom_id not in _seen_symptom_ids:
            SYMPTOMS.append(symptom)
            _seen_symptom_ids.add(symptom_id)

    for rule in data.get("rules", []):
        rule_id = rule["id"]
        if rule_id not in _seen_rule_ids:
            RULES.append(rule)
            _seen_rule_ids.add(rule_id)

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
ORIGINAL_RULES: List[Dict[str, Any]] = []
RULES: List[Dict[str, Any]] = []
DIAGNOSIS_RULES: List[Dict[str, Any]] = []


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
            ORIGINAL_RULES.append(rule)
            _seen_rule_ids.add(rule_id)


for rule in ORIGINAL_RULES:
    has_conclusion = "diagnosis" in rule or "advice" in rule or "severity" in rule
    has_actions = "produces" in rule or "sets" in rule
    if has_conclusion and not has_actions:
        evidence_fact = f"evidence::{rule['id']}"
        evidence_rule = dict(rule)
        evidence_rule["produces"] = {evidence_fact: True}
        evidence_rule["evidence_fact"] = evidence_fact
        RULES.append(evidence_rule)

        diagnosis_rule: Dict[str, Any] = {
            "id": f"diagnosis__{rule['id']}",
            "conditions": {evidence_fact: True},
            "system": rule.get("system"),
            "severity": rule.get("severity"),
            "diagnosis": rule.get("diagnosis"),
            "advice": rule.get("advice"),
            "source_rule": rule.get("id"),
        }
        DIAGNOSIS_RULES.append(diagnosis_rule)
    else:
        RULES.append(rule)

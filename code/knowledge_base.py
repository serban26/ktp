from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


# Determine paths to knowledge base data directory
_BASE_DIR = Path(__file__).resolve().parent
_KB_DIR = _BASE_DIR / "kb_data"


def _load_module(name: str) -> Dict[str, Any]:
    """
    Load a knowledge base module from JSON file.
    
    Args:
        name (str): The module name (without .json extension).
                   Should correspond to a file in the kb_data directory.
    
    Returns:
        Dict[str, Any]: The parsed JSON content as a dictionary.
                       Expected to contain 'systems', 'symptoms', and/or 'rules' keys.
    
    Raises:
        FileNotFoundError: If the module file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    
    Examples:
        >>> data = _load_module("brakes")
        >>> "symptoms" in data
        True
    """
    path = _KB_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# List of all knowledge base modules to load
# Each module covers a different car system or category
_MODULE_NAMES = [
    "general",              # General symptoms and rules
    "engine_ignition",      # Ignition system issues
    "engine_fuel",          # Fuel delivery problems
    "engine_mechanical",    # Mechanical engine issues
    "cooling",              # Cooling system problems
    "brakes",               # Brake system issues
    "wheels",               # Tire and wheel problems
    "steering_suspension",  # Steering and suspension issues
    "transmission",         # Transmission problems
    "climate_ac",           # Climate control and A/C
    "electrical_lighting",  # Electrical and lighting issues
]


# Main knowledge base collections
# These are populated by loading all modules below
CAR_SYSTEMS: List[Dict[str, Any]] = []      # Car system definitions (e.g., brakes, engine)
SYMPTOMS: List[Dict[str, Any]] = []         # Observable symptoms to query
ORIGINAL_RULES: List[Dict[str, Any]] = []   # Original diagnostic rules
RULES: List[Dict[str, Any]] = []            # Processed rules for inference engine
DIAGNOSIS_RULES: List[Dict[str, Any]] = []  # Rules that produce diagnoses


# Track seen IDs to prevent duplicates across modules
_seen_system_ids = set()
_seen_symptom_ids = set()
_seen_rule_ids = set()


# Load all knowledge base modules
for module_name in _MODULE_NAMES:
    data = _load_module(module_name)

    # Add car systems (with duplicate prevention)
    for system in data.get("systems", []):
        system_id = system["id"]
        if system_id not in _seen_system_ids:
            CAR_SYSTEMS.append(system)
            _seen_system_ids.add(system_id)

    # Add symptoms (with duplicate prevention)
    for symptom in data.get("symptoms", []):
        symptom_id = symptom["id"]
        if symptom_id not in _seen_symptom_ids:
            SYMPTOMS.append(symptom)
            _seen_symptom_ids.add(symptom_id)

    # Add rules (with duplicate prevention)
    for rule in data.get("rules", []):
        rule_id = rule["id"]
        if rule_id not in _seen_rule_ids:
            ORIGINAL_RULES.append(rule)
            _seen_rule_ids.add(rule_id)


# Process rules: separate diagnostic conclusions from inference rules
# Diagnostic rules need special handling for the forward chaining engine
for rule in ORIGINAL_RULES:
    # Check if rule has diagnostic output (conclusion)
    has_conclusion = "diagnosis" in rule or "advice" in rule or "severity" in rule
    # Check if rule produces intermediate facts
    has_actions = "produces" in rule or "sets" in rule
    
    if has_conclusion and not has_actions:
        # Create an evidence fact for forward chaining
        # This allows the inference engine to track confirmed diagnoses
        evidence_fact = f"evidence::{rule['id']}"
        evidence_rule = dict(rule)
        evidence_rule["produces"] = {evidence_fact: True}
        evidence_rule["evidence_fact"] = evidence_fact
        RULES.append(evidence_rule)

        # Create separate diagnosis rule for final output
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
        # Rule produces intermediate facts or has no conclusion
        RULES.append(rule)

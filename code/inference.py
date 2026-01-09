from typing import Any, Dict, List, Tuple

from knowledge_base import SYMPTOMS, RULES, CAR_SYSTEMS


SYMPTOM_INDEX: Dict[str, Dict[str, Any]] = {s["id"]: s for s in SYMPTOMS}
SYSTEM_INDEX: Dict[str, Dict[str, Any]] = {s["id"]: s for s in CAR_SYSTEMS}
SEVERITY_RANK: Dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def rule_possible(rule: Dict[str, Any], observations: Dict[str, bool | None]) -> bool:
    conditions: Dict[str, Any] = rule.get("conditions", {})
    for symptom_id, expected in conditions.items():
        value = observations.get(symptom_id)
        if value is None:
            continue
        if bool(value) != bool(expected):
            return False
    return True


def next_symptom_id(candidate_rules: List[Dict[str, Any]], observations: Dict[str, bool | None]) -> str | None:
    stats: Dict[str, int] = {}
    for rule in candidate_rules:
        conditions: Dict[str, Any] = rule.get("conditions", {})
        for symptom_id in conditions.keys():
            if symptom_id in observations:
                continue
            if symptom_id not in SYMPTOM_INDEX:
                continue
            stats[symptom_id] = stats.get(symptom_id, 0) + 1
    if not stats:
        return None
    return max(stats.items(), key=lambda item: (item[1], item[0]))[0]


def rule_score(rule: Dict[str, Any], observations: Dict[str, bool | None]) -> float:
    conditions: Dict[str, Any] = rule.get("conditions", {})
    if not conditions:
        return 0.0
    satisfied = 0
    any_checked = False
    for symptom_id, expected in conditions.items():
        value = observations.get(symptom_id)
        if value is None:
            continue
        any_checked = True
        if bool(value) == bool(expected):
            satisfied += 1
        else:
            return 0.0
    if not any_checked:
        return 0.0
    return satisfied / float(len(conditions))


def infer_diagnoses(observations: Dict[str, bool | None], rules: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    if rules is None:
        rules = RULES

    scored: List[Tuple[float, Dict[str, Any]]] = []
    for rule in rules:
        score = rule_score(rule, observations)
        if score > 0.0:
            scored.append((score, rule))

    def sort_key(item: Tuple[float, Dict[str, Any]]) -> Tuple[float, int, int]:
        score, rule = item
        severity = rule.get("severity", "medium")
        severity_value = SEVERITY_RANK.get(severity, 0)
        conditions = rule.get("conditions", {})
        return (score, severity_value, len(conditions))

    scored.sort(key=sort_key, reverse=True)
    return [rule for score, rule in scored]

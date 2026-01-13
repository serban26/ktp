from typing import Any, Dict, List, Tuple

from knowledge_base import SYMPTOMS, RULES, CAR_SYSTEMS, DIAGNOSIS_RULES, ORIGINAL_RULES


SYMPTOM_INDEX: Dict[str, Dict[str, Any]] = {s["id"]: s for s in SYMPTOMS}
SYSTEM_INDEX: Dict[str, Dict[str, Any]] = {s["id"]: s for s in CAR_SYSTEMS}
ORIGINAL_RULE_INDEX: Dict[str, Dict[str, Any]] = {r["id"]: r for r in ORIGINAL_RULES}

SEVERITY_RANK: Dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def rule_possible(rule: Dict[str, Any], observations: Dict[str, Any]) -> bool:
    conditions: Dict[str, Any] = rule.get("conditions", {})
    for fact_id, expected in conditions.items():
        if fact_id not in observations:
            continue
        value = observations.get(fact_id)
        if value is None:
            continue
        if value != expected:
            return False
    return True


def next_symptom_id(candidate_rules: List[Dict[str, Any]], observations: Dict[str, Any]) -> str | None:
    stats: Dict[str, int] = {}
    for rule in candidate_rules:
        conditions: Dict[str, Any] = rule.get("conditions", {})
        for fact_id in conditions.keys():
            if fact_id in observations:
                continue
            if fact_id not in SYMPTOM_INDEX:
                continue
            stats[fact_id] = stats.get(fact_id, 0) + 1
    if not stats:
        return None
    return max(stats.items(), key=lambda item: (item[1], item[0]))[0]


def rule_score(rule: Dict[str, Any] | None, observations: Dict[str, Any]) -> float:
    if not rule:
        return 0.0
    conditions: Dict[str, Any] = rule.get("conditions", {})
    if not conditions:
        return 0.0
    satisfied = 0
    any_checked = False
    for fact_id, expected in conditions.items():
        if fact_id not in observations:
            continue
        value = observations.get(fact_id)
        if value is None:
            continue
        any_checked = True
        if value == expected:
            satisfied += 1
        else:
            return 0.0
    if not any_checked:
        return 0.0
    return satisfied / max(1, len(conditions))


def _rule_ready_and_true(rule: Dict[str, Any], facts: Dict[str, Any]) -> bool:
    conditions: Dict[str, Any] = rule.get("conditions", {})
    for fact_id, expected in conditions.items():
        if fact_id not in facts:
            return False
        value = facts.get(fact_id)
        if value is None:
            return False
        if value != expected:
            return False
    return True


def forward_chain(initial_facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    facts: Dict[str, Any] = dict(initial_facts)
    fired: List[Dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if not _rule_ready_and_true(rule, facts):
                continue
            updates: Dict[str, Any] = {}
            if isinstance(rule.get("sets"), dict):
                updates.update(rule["sets"])
            if isinstance(rule.get("produces"), dict):
                updates.update(rule["produces"])
            if not updates:
                continue
            local_changed = False
            for k, v in updates.items():
                if facts.get(k) != v:
                    facts[k] = v
                    local_changed = True
            if local_changed:
                fired.append({"rule_id": rule.get("id"), "updates": dict(updates)})
                changed = True
    return facts, fired


def infer_diagnoses(observations: Dict[str, Any], rules: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    if rules is None:
        rules = RULES

    allowed_systems = {r.get("system") for r in rules if r.get("system")}
    if not allowed_systems:
        allowed_systems = None

    facts, fired = forward_chain(observations, rules)

    results: List[Dict[str, Any]] = []
    for src_rule in ORIGINAL_RULES:
        has_conclusion = "diagnosis" in src_rule or "advice" in src_rule or "severity" in src_rule
        if not has_conclusion:
            continue
        if allowed_systems is not None and src_rule.get("system") not in allowed_systems:
            continue
        if not rule_possible(src_rule, observations):
            continue

        score = rule_score(src_rule, observations)
        evidence_fact = f"evidence::{src_rule['id']}"
        confirmed = facts.get(evidence_fact) is True

        if score == 0.0 and not confirmed:
            continue

        result = dict(src_rule)
        result["score"] = score
        result["confirmed"] = confirmed
        result["fired"] = fired
        results.append(result)

    def sort_key(rule: Dict[str, Any]) -> Tuple[int, int, float, int]:
        confirmed_value = 1 if rule.get("confirmed") else 0
        severity = rule.get("severity", "medium")
        severity_value = SEVERITY_RANK.get(severity, 0)
        score = float(rule.get("score", 0.0))
        cond_count = len(rule.get("conditions", {}) or {})
        return (confirmed_value, severity_value, score, cond_count)

    results.sort(key=sort_key, reverse=True)
    return results


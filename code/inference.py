from typing import Any, Dict, List, Tuple

from knowledge_base import SYMPTOMS, RULES, CAR_SYSTEMS


def ask_yes_no(question: str) -> bool | None:
    while True:
        answer = input(question + " ").strip().lower()
        if answer in {"yes", "y"}:
            return True
        if answer in {"no", "n"}:
            return False
        if answer in {"", "skip", "s"}:
            return None
        print("Please answer yes, no, or press Enter to skip.")


SYMPTOM_INDEX: Dict[str, Dict[str, Any]] = {s["id"]: s for s in SYMPTOMS}
SYSTEM_INDEX: Dict[str, Dict[str, Any]] = {s["id"]: s for s in CAR_SYSTEMS}
SEVERITY_RANK: Dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def choose_systems() -> List[str]:
    if not CAR_SYSTEMS:
        return []
    print("Which general area of the car seems most related to the problem?")
    for i, system in enumerate(CAR_SYSTEMS, start=1):
        name = system.get("name", system.get("id", f"System {i}"))
        print(f"{i}. {name}")
    print("Enter one or more numbers separated by commas, or press Enter if you are not sure.")
    while True:
        raw = input("Your choice: ").strip()
        if raw == "":
            return []
        parts = raw.replace(",", " ").split()
        selected: List[str] = []
        for part in parts:
            if not part.isdigit():
                continue
            idx = int(part)
            if 1 <= idx <= len(CAR_SYSTEMS):
                system_id = CAR_SYSTEMS[idx - 1]["id"]
                if system_id not in selected:
                    selected.append(system_id)
        if selected:
            return selected
        print("Please enter valid numbers from the list, or press Enter to skip.")


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
    best_symptom = max(stats.items(), key=lambda item: (item[1], item[0]))[0]
    return best_symptom


def collect_observations_hierarchical() -> Tuple[Dict[str, bool | None], List[Dict[str, Any]]]:
    observations: Dict[str, bool | None] = {}
    print("Please answer some targeted questions about your car.")
    print()
    selected_systems = choose_systems()
    if selected_systems:
        candidate_rules = [r for r in RULES if r.get("system") in selected_systems]
    else:
        candidate_rules = list(RULES)
    while True:
        candidate_rules = [r for r in candidate_rules if rule_possible(r, observations)]
        if not candidate_rules:
            break
        symptom_id = next_symptom_id(candidate_rules, observations)
        if symptom_id is None:
            break
        symptom = SYMPTOM_INDEX.get(symptom_id)
        if symptom is None:
            break
        answer = ask_yes_no(symptom["question"])
        observations[symptom_id] = answer
    return observations, candidate_rules


def collect_observations() -> Dict[str, bool | None]:
    observations, _ = collect_observations_hierarchical()
    return observations


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


def rule_matches(rule: Dict[str, Any], observations: Dict[str, bool | None]) -> bool:
    score = rule_score(rule, observations)
    return score > 0.0


def infer_diagnoses(observations: Dict[str, bool | None], rules: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    rule_set = rules if rules is not None else RULES
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for rule in rule_set:
        score = rule_score(rule, observations)
        if score <= 0.0:
            continue
        scored.append((score, rule))
    def sort_key(item: Tuple[float, Dict[str, Any]]) -> Tuple[float, int, int]:
        score, rule = item
        severity = rule.get("severity", "medium")
        severity_value = SEVERITY_RANK.get(severity, 0)
        conditions = rule.get("conditions", {})
        return (score, severity_value, len(conditions))
    scored.sort(key=sort_key, reverse=True)
    return [rule for score, rule in scored]


def run_session() -> None:
    print("Welcome to the Car Diagnosis Helper.")
    print("This tool cannot replace a professional mechanic,")
    print("but it can help you think about possible causes and next steps.")
    print()
    observations, candidate_rules = collect_observations_hierarchical()
    print()
    print("Thank you. Reasoning about your answers...")
    print()
    matches = infer_diagnoses(observations, candidate_rules)
    if not matches:
        print("I could not find a clear likely cause based on the given information.")
        print("If you are worried about safety, do not drive the car and contact a professional mechanic.")
        return
    print("Possible issues based on your answers:")
    print()
    for i, rule in enumerate(matches, start=1):
        system_id = rule.get("system")
        system_name = system_id
        if system_id in SYSTEM_INDEX:
            system_name = SYSTEM_INDEX[system_id].get("name", system_id)
        severity = rule.get("severity", "medium")
        score = rule_score(rule, observations)
        percent = int(round(score * 100))
        print(f"{i}. [{system_name}] ({severity}) {rule['diagnosis']}")
        print(f"   Match based on your answers: about {percent}% of this diagnosis' key symptoms match.")
        print(f"   Suggested next step: {rule['advice']}")
        print()
    print("Remember: this is only a support tool. When in doubt, consult a professional mechanic.")


if __name__ == "__main__":
    run_session()

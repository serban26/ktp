from typing import Any, Dict, List

from knowledge_base import SYMPTOMS, RULES


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


def collect_observations() -> Dict[str, bool | None]:
    observations: Dict[str, bool | None] = {}
    print("Please answer the following questions about your car.")
    print()
    for symptom in SYMPTOMS:
        symptom_id = symptom["id"]
        question = symptom["question"]
        answer = ask_yes_no(question)
        observations[symptom_id] = answer
    return observations


def rule_matches(rule: Dict[str, Any], observations: Dict[str, bool | None]) -> bool:
    conditions: Dict[str, Any] = rule.get("conditions", {})
    any_checked = False
    for symptom_id, expected in conditions.items():
        value = observations.get(symptom_id)
        if value is None:
            continue
        any_checked = True
        if bool(value) != bool(expected):
            return False
    return any_checked


def infer_diagnoses(observations: Dict[str, bool | None]) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for rule in RULES:
        if rule_matches(rule, observations):
            matches.append(rule)
    return matches


def run_session() -> None:
    print("Welcome to the Car Diagnosis Helper.")
    print("This tool cannot replace a professional mechanic,")
    print("but it can help you think about possible causes and next steps.")
    print()
    observations = collect_observations()
    print()
    print("Thank you. Reasoning about your answers...")
    print()
    matches = infer_diagnoses(observations)
    if not matches:
        print("I could not find a clear likely cause based on the given information.")
        print("If you are worried about safety, do not drive the car and contact a professional mechanic.")
        return
    print("Possible issues based on your answers:")
    print()
    for i, rule in enumerate(matches, start=1):
        print(f"{i}. {rule['diagnosis']}")
        print(f"   Suggested next step: {rule['advice']}")
        print()
    print("Remember: this is only a support tool. When in doubt, consult a professional mechanic.")


if __name__ == "__main__":
    run_session()

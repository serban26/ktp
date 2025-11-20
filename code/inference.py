from typing import Dict, List, Any

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
    print("I will ask a few short questions about your car.")
    print("If you are not sure about a question, just press Enter to skip it.")
    observations: Dict[str, bool | None] = {}
    for symptom in SYMPTOMS:
        answer = ask_yes_no(symptom["question"])
        observations[symptom["id"]] = answer
    return observations


def rule_matches(rule: Dict[str, Any], observations: Dict[str, bool | None]) -> bool:
    for key, expected in rule["conditions"].items():
        value = observations.get(key)
        if value is None:
            return False
        if value is not expected:
            return False
    return True


def infer_diagnoses(observations: Dict[str, bool | None]) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for rule in RULES:
        if rule_matches(rule, observations):
            matches.append(rule)
    return matches


def run_session() -> None:
    print("Welcome to the Car Diagnosis Helper.")
    print("This tool cannot replace a professional mechanic,")
    print("but it can help you think about possible causes and next steps.\n")
    observations = collect_observations()
    print("\nThank you. Reasoning about your answers...\n")
    matches = infer_diagnoses(observations)
    if not matches:
        print("I could not find a clear likely cause based on the given information.")
        print("If you are worried about safety, do not drive the car and contact a professional mechanic.")
        return
    print("Possible issues based on your answers:\n")
    for i, rule in enumerate(matches, start=1):
        print(f"{i}. {rule['diagnosis']}")
        print(f"   Suggested next step: {rule['advice']}\n")
    print("Remember: this is only a support tool. When in doubt, consult a professional mechanic.")

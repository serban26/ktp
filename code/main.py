from typing import Any, Dict, List

import streamlit as st

from knowledge_base import CAR_SYSTEMS, RULES
from inference import SYMPTOM_INDEX, SYSTEM_INDEX, rule_possible, next_symptom_id, rule_score, infer_diagnoses


def initialize_state() -> None:
    if "selected_system_ids" not in st.session_state:
        st.session_state.selected_system_ids = []
    if "observations" not in st.session_state:
        st.session_state.observations = {}
    if "candidate_rules" not in st.session_state:
        st.session_state.candidate_rules = []
    if "current_symptom_id" not in st.session_state:
        st.session_state.current_symptom_id = None
    if "finished" not in st.session_state:
        st.session_state.finished = False
    if "matches" not in st.session_state:
        st.session_state.matches = []


def reset_session() -> None:
    st.session_state.observations = {}
    st.session_state.candidate_rules = []
    st.session_state.current_symptom_id = None
    st.session_state.finished = False
    st.session_state.matches = []


def start_session() -> None:
    reset_session()
    selected_ids: List[str] = []
    for system in CAR_SYSTEMS:
        system_id = system["id"]
        if st.session_state.get(f"sys_{system_id}", False):
            selected_ids.append(system_id)
    st.session_state.selected_system_ids = selected_ids
    if selected_ids:
        st.session_state.candidate_rules = [r for r in RULES if r.get("system") in selected_ids]
    else:
        st.session_state.candidate_rules = list(RULES)
    select_next_question()


def select_next_question() -> None:
    observations: Dict[str, bool | None] = st.session_state.observations
    candidate_rules: List[Dict[str, Any]] = [
        r for r in st.session_state.candidate_rules if rule_possible(r, observations)
    ]
    st.session_state.candidate_rules = candidate_rules
    if not candidate_rules:
        st.session_state.current_symptom_id = None
        st.session_state.finished = True
        compute_matches()
        return
    symptom_id = next_symptom_id(candidate_rules, observations)
    if symptom_id is None:
        st.session_state.current_symptom_id = None
        st.session_state.finished = True
        compute_matches()
        return
    st.session_state.current_symptom_id = symptom_id


def record_answer_yes() -> None:
    record_answer(True)


def record_answer_no() -> None:
    record_answer(False)


def record_answer_skip() -> None:
    record_answer(None)


def record_answer(value: bool | None) -> None:
    symptom_id = st.session_state.current_symptom_id
    if symptom_id is None:
        return
    observations: Dict[str, bool | None] = st.session_state.observations
    observations[symptom_id] = value
    st.session_state.observations = observations
    select_next_question()


def compute_matches() -> None:
    observations: Dict[str, bool | None] = st.session_state.observations
    candidate_rules: List[Dict[str, Any]] = st.session_state.candidate_rules
    matches = infer_diagnoses(observations, candidate_rules)
    st.session_state.matches = matches


def main() -> None:
    initialize_state()
    st.title("Car Diagnosis Helper")
    st.caption("Interactive expert system to help you reason about possible car issues. Not a replacement for a mechanic.")

    st.markdown("---")
    st.subheader("1. Select the areas that seem related to the problem")

    cols = st.columns(3)
    for i, system in enumerate(CAR_SYSTEMS):
        name = system.get("name", system["id"])
        description = system.get("description", "")
        col = cols[i % len(cols)]
        with col:
            st.checkbox(name, key=f"sys_{system['id']}")
            if description:
                st.caption(description)

    st.markdown("---")

    if st.button("Start new diagnosis"):
        start_session()

    if st.session_state.current_symptom_id is not None and not st.session_state.finished:
        symptom_id = st.session_state.current_symptom_id
        symptom = SYMPTOM_INDEX.get(symptom_id)
        if symptom is not None:
            st.subheader("2. Answer the questions")
            with st.container(border=True):
                st.markdown("**Current question**")
                st.write(symptom["question"])
                col_yes, col_no, col_skip = st.columns(3)
                col_yes.button("Yes", key="answer_yes", on_click=record_answer_yes)
                col_no.button("No", key="answer_no", on_click=record_answer_no)
                col_skip.button("Skip", key="answer_skip", on_click=record_answer_skip)
    elif not st.session_state.finished:
        st.info("Select one or more areas above and click **Start new diagnosis** to begin.")

    if st.session_state.observations:
        st.markdown("---")
        st.subheader("Your answers so far")
        for symptom_id, value in st.session_state.observations.items():
            symptom = SYMPTOM_INDEX.get(symptom_id)
            label = symptom["question"] if symptom is not None else symptom_id
            if value is True:
                answer_label = "Yes"
            elif value is False:
                answer_label = "No"
            else:
                answer_label = "Skipped"
            st.markdown(f"- {label} — **{answer_label}**")

    if st.session_state.finished:
        st.markdown("---")
        st.subheader("3. Possible issues")
        if not st.session_state.matches:
            st.warning("No clear diagnosis could be found from the current answers.")
        else:
            for rule in st.session_state.matches:
                system_id = rule.get("system")
                system_name = system_id
                if system_id in SYSTEM_INDEX:
                    system_name = SYSTEM_INDEX[system_id].get("name", system_id)
                severity = rule.get("severity", "medium")
                score = rule_score(rule, st.session_state.observations)
                percent = int(round(score * 100))
                with st.container(border=True):
                    st.markdown(f"**{system_name}**  ·  Severity: `{severity}`")
                    st.markdown(f"*{rule['diagnosis']}*")
                    st.progress(min(max(percent, 0), 100))
                    st.caption(f"Approximate match: {percent}% of key symptoms.")
                    st.write(rule["advice"])
        if st.button("Start over"):
            reset_session()

    st.markdown("---")
    st.caption("When in doubt about safety, do not drive the car and contact a professional mechanic.")


if __name__ == "__main__":
    main()

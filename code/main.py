from typing import Any, Dict, List

import streamlit as st

from knowledge_base import CAR_SYSTEMS, RULES
from inference import SYMPTOM_INDEX, SYSTEM_INDEX, rule_possible, next_symptom_id, rule_score, infer_diagnoses


def initialize_state() -> None:
    """
    Initialize Streamlit session state variables if not already set.
    
    This function ensures all required session state variables exist before
    the app tries to use them. Should be called at the start of main().
    
    Session State Variables Created:
        - selected_system_ids (List[str]): IDs of car systems user selected
        - observations (Dict[str, bool | None]): User's answers to symptom questions
        - candidate_rules (List[Dict]): Rules still under consideration
        - current_symptom_id (str | None): ID of symptom currently being asked about
        - finished (bool): Whether the diagnosis session is complete
        - matches (List[Dict]): Final list of matching diagnoses
    
    Returns:
        None
    
    Note:
        This follows Streamlit's session state pattern for maintaining state
        across reruns caused by user interactions.
    """
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
    """
    Clear all diagnosis session data to start fresh.
    
    Resets the session to allow starting a new diagnosis from scratch.
    Preserves the selected car systems but clears all observations and results.
    
    Returns:
        None
    
    Side Effects:
        Modifies st.session_state by clearing:
        - observations
        - candidate_rules
        - current_symptom_id
        - finished flag
        - matches
    """
    st.session_state.observations = {}
    st.session_state.candidate_rules = []
    st.session_state.current_symptom_id = None
    st.session_state.finished = False
    st.session_state.matches = []


def start_session() -> None:
    """
    Begin a new diagnosis session.
    Filters rules based on selected car systems and picks first question.
    
    This function is called when the user clicks "Start new diagnosis".
    It reads which car systems the user selected (if any), filters the rule
    base accordingly, and initiates the question-asking process.
    
    Returns:
        None
    
    Side Effects:
        - Calls reset_session() to clear previous data
        - Updates st.session_state.selected_system_ids
        - Updates st.session_state.candidate_rules
        - Calls select_next_question() to pick first question
    
    Note:
        If no systems are selected, all rules are considered (general diagnosis).
        If specific systems are selected, only rules for those systems are used.
    """
    reset_session()
    selected_ids: List[str] = []
    # Collect which car systems user selected
    for system in CAR_SYSTEMS:
        system_id = system["id"]
        if st.session_state.get(f"sys_{system_id}", False):
            selected_ids.append(system_id)
    st.session_state.selected_system_ids = selected_ids
    # Filter rules to only selected systems
    if selected_ids:
        st.session_state.candidate_rules = [r for r in RULES if r.get("system") in selected_ids]
    else:
        # No systems selected means use all rules
        st.session_state.candidate_rules = list(RULES)
    # Pick the first question to ask
    select_next_question()


def select_next_question() -> None:
    """
    Determine the next most informative symptom to ask about.
    If no questions remain, finalize the diagnosis.
    
    This function implements the question selection strategy:
    1. Filter candidate rules to only those still possible
    2. If no rules remain, mark session as finished
    3. Use next_symptom_id() to pick the most informative question
    4. If no questions remain, mark session as finished
    
    Returns:
        None
    
    Side Effects:
        Updates st.session_state with:
        - candidate_rules: Updated list after filtering
        - current_symptom_id: The next symptom to ask about
        - finished: Set to True if diagnosis is complete
        Calls compute_matches() when diagnosis is finished.
    
    Algorithm:
        Uses greedy best-first search with frequency heuristic.
        Asks about symptoms that appear in the most candidate rules,
        maximizing information gain per question.
    """
    observations: Dict[str, bool | None] = st.session_state.observations
    # Filter to rules still possible given current observations
    candidate_rules: List[Dict[str, Any]] = [
        r for r in st.session_state.candidate_rules if rule_possible(r, observations)
    ]
    st.session_state.candidate_rules = candidate_rules
    # No candidate rules left - we're done
    if not candidate_rules:
        st.session_state.current_symptom_id = None
        st.session_state.finished = True
        compute_matches()
        return
    # Ask the most informative symptom next
    symptom_id = next_symptom_id(candidate_rules, observations)
    # No more questions to ask - we're done
    if symptom_id is None:
        st.session_state.current_symptom_id = None
        st.session_state.finished = True
        compute_matches()
        return
    st.session_state.current_symptom_id = symptom_id


def record_answer_yes() -> None:
    """
    Record a 'yes' answer to current symptom question.
    
    Button callback for the "Yes" button in the UI.
    
    Returns:
        None
    """
    record_answer(True)


def record_answer_no() -> None:
    """
    Record a 'no' answer to current symptom question.
    
    Button callback for the "No" button in the UI.
    
    Returns:
        None
    """
    record_answer(False)


def record_answer_skip() -> None:
    """
    Record that user skipped the current symptom question.
    
    Button callback for the "Skip" button in the UI.
    
    Returns:
        None
    """
    record_answer(None)


def record_answer(value: bool | None) -> None:
    """
    Record user's answer to current symptom and move to next question.
    
    This is the core function for capturing user responses during diagnosis.
    It stores the answer in the observations dict and triggers selection
    of the next question.
    
    Args:
        value (bool | None): The user's response:
                            - True: User confirmed the symptom (Yes)
                            - False: User denied the symptom (No)
                            - None: User skipped the question (uncertain)
    
    Returns:
        None
    
    Side Effects:
        - Updates st.session_state.observations with the new answer
        - Calls select_next_question() to continue the diagnosis
    
    Note:
        If current_symptom_id is None, this function does nothing (defensive coding).
    """
    symptom_id = st.session_state.current_symptom_id
    if symptom_id is None:
        return
    observations: Dict[str, bool | None] = st.session_state.observations
    observations[symptom_id] = value
    st.session_state.observations = observations
    # Move to next question
    select_next_question()


def compute_matches() -> None:
    """
    Run inference to find matching diagnoses based on observations.
    
    Called when the diagnosis session is complete (no more questions to ask).
    Invokes the inference engine to generate a ranked list of possible diagnoses.
    
    Returns:
        None
    
    Side Effects:
        Updates st.session_state.matches with the list of diagnoses returned
        by infer_diagnoses().
    
    Note:
        The matches are sorted by relevance (confirmed > severity > score).
    """
    observations: Dict[str, bool | None] = st.session_state.observations
    candidate_rules: List[Dict[str, Any]] = st.session_state.candidate_rules
    matches = infer_diagnoses(observations, candidate_rules)
    st.session_state.matches = matches


def main() -> None:
    """
    Main Streamlit app entry point - builds the UI.
    
    Constructs the complete user interface for the Car Diagnosis Helper.
    Handles all three phases of the diagnosis workflow:
    1. System selection: User picks which car systems to focus on (optional)
    2. Question answering: Interactive yes/no questions about symptoms
    3. Results display: Shows matching diagnoses with severity and advice
    
    Returns:
        None
    
    UI Components:
        - Title and warning caption
        - Checkbox grid for car system selection
        - "Start new diagnosis" button
        - Dynamic question interface (yes/no/skip buttons)
        - Answer summary list
        - Diagnosis results with severity, confidence scores, and advice
        - "Start over" button
    
    State Management:
        Uses Streamlit's session_state to maintain:
        - Selected car systems
        - User's observations/answers
        - Current question being asked
        - Diagnosis completion status
        - Final diagnosis results
    
    Note:
        This function is called on every Streamlit rerun (triggered by user interaction).
        Session state preserves data across reruns.
    """
    st.set_page_config(page_title="Car Diagnosis Helper", page_icon="🚗", layout="wide")

    initialize_state()

    st.title("Car Diagnosis Helper")
    st.caption(
        "This tool cannot replace a professional mechanic. If there is any safety concern, stop driving and seek help."
    )

    # Step 1: System selection
    st.subheader("1. Select the areas that seem related (optional)")
    st.write(
        "You can select one or more subsystems to focus the questions. If you are not sure, leave everything unselected."
    )

    # Display car systems in columns
    cols = st.columns(3)
    for i, system in enumerate(CAR_SYSTEMS):
        name = system.get("name", system.get("id", "Unknown"))
        description = system.get("description", "")
        col = cols[i % len(cols)]
        with col:
            st.checkbox(name, key=f"sys_{system['id']}")
            if description:
                st.caption(description)

    st.markdown("---")

    # Button to start new diagnosis
    if st.button("Start new diagnosis"):
        start_session()

    # Step 2: Question asking interface
    if st.session_state.current_symptom_id is not None and not st.session_state.finished:
        symptom_id = st.session_state.current_symptom_id
        symptom = SYMPTOM_INDEX.get(symptom_id)
        if symptom is not None:
            st.subheader("2. Answer the questions")
            with st.container(border=True):
                st.markdown("**Current question**")
                st.write(symptom["question"])
                # Three buttons for yes/no/skip
                col_yes, col_no, col_skip = st.columns(3)
                col_yes.button("Yes", key=f"answer_yes_{symptom_id}", on_click=record_answer_yes)
                col_no.button("No", key=f"answer_no_{symptom_id}", on_click=record_answer_no)
                col_skip.button("Skip", key=f"answer_skip_{symptom_id}", on_click=record_answer_skip)
    elif not st.session_state.finished:
        st.info("Select one or more areas above and click **Start new diagnosis** to begin.")

    # Display answers collected so far
    if st.session_state.observations:
        st.markdown("---")
        st.subheader("Your answers so far")
        for symptom_id, value in st.session_state.observations.items():
            symptom = SYMPTOM_INDEX.get(symptom_id, {})
            label = symptom.get("label") or symptom.get("question") or symptom_id
            if value is True:
                answer_label = "Yes"
            elif value is False:
                answer_label = "No"
            else:
                answer_label = "Skipped"
            st.markdown(f"- {label} — **{answer_label}**")

    # Step 3: Display results when finished
    if st.session_state.finished:
        st.markdown("---")
        st.subheader("3. Possible issues")
        if not st.session_state.matches:
            st.warning("No clear diagnosis could be found from the current answers.")
        else:
            # Display each matched diagnosis
            for rule in st.session_state.matches:
                system_id = rule.get("system")
                system_name = system_id
                if system_id in SYSTEM_INDEX:
                    system_name = SYSTEM_INDEX[system_id].get("name", system_id)
                severity = rule.get("severity", "medium")
                score = float(rule.get("score", rule_score(rule, st.session_state.observations)))
                percent = int(round(score * 100))
                with st.container(border=True):
                    st.markdown(f"**{system_name}**  ·  Severity: `{severity}`")
                    st.markdown(f"*{rule['diagnosis']}*")
                    # Show confidence score as progress bar
                    st.progress(min(max(percent, 0), 100))
                    st.caption(f"Approximate match: {percent}% of key symptoms.")
                    st.write(rule["advice"])
        # Button to start over
        if st.button("Start over"):
            reset_session()

    st.markdown("---")
    st.caption("When in doubt about safety, do not drive the car and contact a professional mechanic.")


if __name__ == "__main__":
    main()

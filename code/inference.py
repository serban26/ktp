from typing import Any, Dict, List, Tuple

from knowledge_base import SYMPTOMS, RULES, CAR_SYSTEMS, DIAGNOSIS_RULES, ORIGINAL_RULES


# Create lookup dictionaries for fast access by ID
SYMPTOM_INDEX: Dict[str, Dict[str, Any]] = {s["id"]: s for s in SYMPTOMS}
SYSTEM_INDEX: Dict[str, Dict[str, Any]] = {s["id"]: s for s in CAR_SYSTEMS}
ORIGINAL_RULE_INDEX: Dict[str, Dict[str, Any]] = {r["id"]: r for r in ORIGINAL_RULES}

# Severity ranking for sorting diagnoses by importance
SEVERITY_RANK: Dict[str, int] = {
    "critical": 4,  # Most urgent, safety-critical issues
    "high": 3,      # Important issues requiring prompt attention
    "medium": 2,    # Should be addressed but not urgent
    "low": 1,       # Minor issues or maintenance items
}


def rule_possible(rule: Dict[str, Any], observations: Dict[str, Any]) -> bool:
    """
    Check if a rule is still possible given current observations.
    
    Args:
        rule (Dict[str, Any]): A diagnostic rule containing conditions to check.
                               Must have a 'conditions' key with symptom ID to expected value mappings.
        observations (Dict[str, Any]): User's observed symptoms mapped to their values.
                                      Values can be True, False, or None (skipped).
    
    Returns:
        bool: True if the rule is still possible (no contradictions found),
              False if any observed symptom contradicts a rule condition.
    
    Examples:
        >>> rule = {"conditions": {"engine_cranks": True, "lights_dim": False}}
        >>> observations = {"engine_cranks": True}
        >>> rule_possible(rule, observations)
        True
        >>> observations = {"engine_cranks": False}
        >>> rule_possible(rule, observations)
        False
    """
    conditions: Dict[str, Any] = rule.get("conditions", {})
    # Iterate through each condition required by the rule
    for fact_id, expected in conditions.items():
        # Skip conditions we haven't asked about yet
        if fact_id not in observations:
            continue
        value = observations.get(fact_id)
        # Skip conditions where user answered "skip"
        if value is None:
            continue
        # If observed value contradicts expected value, rule is impossible
        if value != expected:
            return False
    # Rule is still possible if no contradictions found
    return True


def next_symptom_id(candidate_rules: List[Dict[str, Any]], observations: Dict[str, Any]) -> str | None:
    """
    Select the most informative symptom to ask about next.
    Uses frequency heuristic: choose symptom that appears in most candidate rules.
    
    Args:
        candidate_rules (List[Dict[str, Any]]): List of rules still under consideration.
                                                Each rule has a 'conditions' dict of required symptoms.
        observations (Dict[str, Any]): Symptoms already observed/asked about.
                                      Used to filter out symptoms that don't need to be asked again.
    
    Returns:
        str | None: The symptom ID that appears most frequently in candidate rules,
                    or None if no more symptoms need to be asked.
                    Ties are broken alphabetically by symptom ID.
    
    Note:
        This implements a greedy best-first search strategy for question selection.
        The symptom that appears in the most rules is likely to eliminate the most
        uncertainty with a single question.
    """
    stats: Dict[str, int] = {}
    # Count how many rules need each symptom
    for rule in candidate_rules:
        conditions: Dict[str, Any] = rule.get("conditions", {})
        for fact_id in conditions.keys():
            # Skip symptoms already observed
            if fact_id in observations:
                continue
            # Skip if not a valid symptom (might be an intermediate fact)
            if fact_id not in SYMPTOM_INDEX:
                continue
            # Increment count for this symptom
            stats[fact_id] = stats.get(fact_id, 0) + 1
    # No more symptoms to ask about
    if not stats:
        return None
    # Return symptom with highest count (ties broken alphabetically)
    return max(stats.items(), key=lambda item: (item[1], item[0]))[0]


def rule_score(rule: Dict[str, Any] | None, observations: Dict[str, Any]) -> float:
    """
    Calculate a confidence score (0.0 to 1.0) for how well observations match a rule.
    Returns 0.0 if any condition contradicts observations.
    
    Args:
        rule (Dict[str, Any] | None): The diagnostic rule to score.
                                      Must contain a 'conditions' dict mapping symptom IDs to expected values.
                                      If None, returns 0.0.
        observations (Dict[str, Any]): The observed symptoms and their values.
                                      Values can be True, False, or None (skipped).
    
    Returns:
        float: A score between 0.0 and 1.0 representing confidence in the diagnosis:
               - 1.0: All rule conditions have been checked and match observations
               - 0.5: Half of the conditions match (partial evidence)
               - 0.0: No conditions checked, or any condition contradicts observations
    
    Note:
        The score is calculated as: (satisfied_conditions / total_conditions)
        Only observed symptoms are counted; unasked symptoms don't affect the score.
        A single contradiction immediately returns 0.0 (rule is impossible).
    
    Examples:
        >>> rule = {"conditions": {"a": True, "b": True, "c": False}}
        >>> rule_score(rule, {"a": True, "b": True})  # 2/3 conditions satisfied
        0.666...
        >>> rule_score(rule, {"a": False})  # Contradiction
        0.0
    """
    if not rule:
        return 0.0
    conditions: Dict[str, Any] = rule.get("conditions", {})
    if not conditions:
        return 0.0
    satisfied = 0  # Count of conditions that match observations
    any_checked = False  # Track if we checked any conditions
    # Check each condition against observations
    for fact_id, expected in conditions.items():
        # Skip conditions we haven't observed
        if fact_id not in observations:
            continue
        value = observations.get(fact_id)
        # Skip skipped questions
        if value is None:
            continue
        any_checked = True
        if value == expected:
            satisfied += 1
        else:
            # Any contradiction means score is 0
            return 0.0
    # No observations checked means no score
    if not any_checked:
        return 0.0
    # Return proportion of conditions satisfied
    return satisfied / max(1, len(conditions))


def _rule_ready_and_true(rule: Dict[str, Any], facts: Dict[str, Any]) -> bool:
    """
    Check if all conditions of a rule are satisfied (ready to fire).
    Used by forward chaining engine.
    
    Args:
        rule (Dict[str, Any]): A rule from the knowledge base.
                              Must contain a 'conditions' dict with required facts.
        facts (Dict[str, Any]): The current fact base (working memory).
                               Maps fact IDs to their values.
    
    Returns:
        bool: True if all of the rule's conditions are present in facts and match
              their expected values. False otherwise.
    
    Note:
        This is stricter than rule_possible() - it requires ALL conditions to be
        known (not None) and match exactly. Used to determine when a rule should
        fire during forward chaining inference.
    """
    conditions: Dict[str, Any] = rule.get("conditions", {})
    # All conditions must be present and match expected values
    for fact_id, expected in conditions.items():
        # Condition not yet established
        if fact_id not in facts:
            return False
        value = facts.get(fact_id)
        # Value is unknown
        if value is None:
            return False
        # Value contradicts expected
        if value != expected:
            return False
    # All conditions satisfied
    return True


def forward_chain(initial_facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Forward chaining inference engine.
    Repeatedly applies rules to derive new facts until no more rules can fire.
    
    Args:
        initial_facts (Dict[str, Any]): Initial set of known facts (observations from user).
                                        Maps fact IDs to their values.
        rules (List[Dict[str, Any]]): List of inference rules to apply.
                                     Each rule has 'conditions' (what must be true to fire)
                                     and 'sets'/'produces' (what facts to assert when fired).
    
    Returns:
        Tuple[Dict[str, Any], List[Dict[str, Any]]]: A tuple containing:
            - facts: The final fact base after all rules have been applied
            - fired: List of dicts describing which rules fired and what they produced,
                    each with keys 'rule_id' and 'updates'
    
    Algorithm:
        1. Start with initial_facts as the working memory
        2. Iterate through all rules, checking if conditions are satisfied
        3. When a rule fires, add its produced facts to working memory
        4. Repeat until no new facts can be derived (fixed point reached)
    
    Note:
        This implements a classic forward chaining algorithm (data-driven reasoning).
        The algorithm is guaranteed to terminate because:
        - Each rule can only produce a finite set of facts
        - Facts are only added, never removed
        - A rule only fires if it produces NEW facts
    
    Examples:
        >>> facts = {"has_fever": True, "has_cough": True}
        >>> rules = [{"conditions": {"has_fever": True}, "produces": {"symptom_count": 1}}]
        >>> result_facts, fired = forward_chain(facts, rules)
        >>> "symptom_count" in result_facts
        True
    """
    # Start with initial observations
    facts: Dict[str, Any] = dict(initial_facts)
    fired: List[Dict[str, Any]] = []  # Track which rules fired
    changed = True
    # Keep applying rules until no new facts are derived
    while changed:
        changed = False
        for rule in rules:
            # Check if rule conditions are satisfied
            if not _rule_ready_and_true(rule, facts):
                continue
            # Collect facts this rule produces
            updates: Dict[str, Any] = {}
            if isinstance(rule.get("sets"), dict):
                updates.update(rule["sets"])
            if isinstance(rule.get("produces"), dict):
                updates.update(rule["produces"])
            # Skip rules that don't produce new facts
            if not updates:
                continue
            # Apply updates to fact base
            local_changed = False
            for k, v in updates.items():
                if facts.get(k) != v:
                    facts[k] = v
                    local_changed = True
            # Track that this rule fired
            if local_changed:
                fired.append({"rule_id": rule.get("id"), "updates": dict(updates)})
                changed = True
    return facts, fired


def infer_diagnoses(observations: Dict[str, Any], rules: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    """
    Main inference function: combines forward chaining with scoring.
    Returns list of possible diagnoses sorted by relevance and severity.
    
    Args:
        observations (Dict[str, Any]): User's observed symptoms.
                                       Maps symptom IDs to True/False/None values.
        rules (List[Dict[str, Any]] | None, optional): Rules to consider for diagnosis.
                                                       If None, uses all rules from RULES.
                                                       Defaults to None.
    
    Returns:
        List[Dict[str, Any]]: List of matching diagnostic rules, sorted by priority.
                             Each dict contains:
                             - 'id': Rule identifier
                             - 'diagnosis': Human-readable diagnosis
                             - 'advice': Recommended next steps
                             - 'severity': 'critical', 'high', 'medium', or 'low'
                             - 'score': Confidence score (0.0 to 1.0)
                             - 'confirmed': Whether forward chaining confirmed this diagnosis
                             - 'fired': List of intermediate rules that fired
                             - 'system': The car system this diagnosis relates to
    
    Algorithm:
        1. Run forward chaining to derive intermediate facts from observations
        2. Filter diagnostic rules by selected car systems
        3. Check each diagnostic rule for possibility given observations
        4. Calculate confidence score for each possible diagnosis
        5. Sort by: confirmed status > severity > score > condition count
    
    Note:
        This hybrid approach combines:
        - Forward chaining: Derives intermediate facts using inference rules
        - Pattern matching: Directly matches observations against diagnostic rules
        - Scoring: Ranks partial matches by confidence level
        
        The system can handle uncertainty (skipped questions) and partial information.
    
    Examples:
        >>> obs = {"engine_cranks": False, "lights_dim": True}
        >>> diagnoses = infer_diagnoses(obs)
        >>> len(diagnoses) > 0
        True
        >>> diagnoses[0]['severity'] in ['critical', 'high', 'medium', 'low']
        True
    """
    if rules is None:
        rules = RULES

    # Determine which car systems are in scope
    allowed_systems = {r.get("system") for r in rules if r.get("system")}
    if not allowed_systems:
        allowed_systems = None

    # Run forward chaining to derive intermediate facts
    facts, fired = forward_chain(observations, rules)

    # Collect all matching diagnostic rules
    results: List[Dict[str, Any]] = []
    for src_rule in ORIGINAL_RULES:
        # Only consider rules that have diagnostic conclusions
        has_conclusion = "diagnosis" in src_rule or "advice" in src_rule or "severity" in src_rule
        if not has_conclusion:
            continue
        # Filter by selected car systems
        if allowed_systems is not None and src_rule.get("system") not in allowed_systems:
            continue
        # Skip rules contradicted by observations
        if not rule_possible(src_rule, observations):
            continue

        # Calculate confidence score
        score = rule_score(src_rule, observations)
        # Check if forward chaining confirmed this diagnosis
        evidence_fact = f"evidence::{src_rule['id']}"
        confirmed = facts.get(evidence_fact) is True

        # Skip rules with no evidence
        if score == 0.0 and not confirmed:
            continue

        # Add diagnosis to results with metadata
        result = dict(src_rule)
        result["score"] = score
        result["confirmed"] = confirmed
        result["fired"] = fired
        results.append(result)

    def sort_key(rule: Dict[str, Any]) -> Tuple[int, int, float, int]:
        """Sort diagnoses by: confirmed status, severity, score, condition count."""
        confirmed_value = 1 if rule.get("confirmed") else 0
        severity = rule.get("severity", "medium")
        severity_value = SEVERITY_RANK.get(severity, 0)
        score = float(rule.get("score", 0.0))
        cond_count = len(rule.get("conditions", {}) or {})
        return (confirmed_value, severity_value, score, cond_count)

    # Sort diagnoses: most relevant and severe first
    results.sort(key=sort_key, reverse=True)
    return results


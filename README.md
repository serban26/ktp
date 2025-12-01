# Car Diagnosis Helper - Knowledge-Based Car Troubleshooter

## Overview

Car Diagnosis Helper is a small but complete knowledge-based system that helps car owners reason about simple car problems based on observable symptoms. The system asks a structured series of questions and uses explicit rules to suggest likely causes and possible next steps.

The goal is not to replace a professional mechanic, but to support car owners in:
- deciding whether it is likely safe to keep driving, and  
- having a clearer description of the problem when contacting a garage.

The core knowledge comes from an experienced car mechanic and is stored in a modular Python knowledge base. Each car subsystem (brakes, cooling, ignition, fuel, wheels, steering, etc.) has its own file defining symptoms and rules, which are aggregated into one unified knowledge base for inference.

## Running the system

Requirements:

- Python 3.13 or higher

Steps:

1. Clone this repository.
2. In the project directory, run:

   ```bash
   python code/main.py
   ```

3. Answer the questions with `yes`, `no`, or press `Enter` to skip if you are unsure.
4. At the end, the system will display one or more possible issues and suggested next steps, ordered roughly by severity and grouped by subsystem.

## Project structure

All source code lives in the `code/` directory:

- `code/main.py` - entry point that starts an interactive diagnosis session in the console.
- `code/inference.py` - inference engine that matches user answers to rules and produces diagnoses.
- `code/knowledge_base/` - modular knowledge base package:
  - `__init__.py` - aggregates all symptom and rule sets into flat `SYMPTOMS` and `RULES` lists without duplicates.
  - `general.py` - shared `CAR_SYSTEMS` list and general symptoms/rules that cut across subsystems.
  - `engine_ignition.py` - ignition-related symptoms and rules (e.g. misfires, no-start with spark issues).
  - `engine_fuel.py` - fuel delivery and injection symptoms and rules (e.g. rich mixture, hesitation).
  - `engine_mechanical.py` - mechanical engine symptoms and rules (e.g. knocking, compression-related behaviour).
  - `cooling.py` - coolant and overheating-related symptoms and rules (e.g. high temperature, sweet smell).
  - `brakes.py` - brake system symptoms and rules (hydraulic and mechanical).
  - `wheels.py` - wheels and tyre-related symptoms and rules (vibration, uneven wear).
  - `steering_suspension.py` - steering and suspension symptoms and rules (pulling, clunks over bumps).
  - `transmission.py` - transmission and clutch symptoms and rules (slipping, gear engagement problems).
  - `climate_ac.py` - climate control and air conditioning symptoms and rules.
  - `electrical_lighting.py` - lighting and basic electrical symptoms and rules.

The knowledge base modules only contain declarative data structures (symptoms, rules and car system identifiers). All procedural code for asking questions and performing inference lives in `main.py` and `inference.py`.

## Knowledge representation

### Symptoms

Symptoms are small dictionaries with an `id` and a natural-language `question`, for example:

```python
{
    "id": "engine_cranks",
    "question": "When you try to start the car, does the engine crank or turn over? (yes/no)",
}
```

Each symptom is designed to be observable without tools by an average driver (starting behaviour, lights, noises, smells, vibrations, performance changes).

### Rules

Rules are dictionaries with:

- `id` - unique rule identifier,
- `conditions` - mapping from symptom ids to expected boolean values,
- `system` - affected car subsystem identifier (from `CAR_SYSTEMS`),
- `severity` - one of `low`, `medium`, `high`, `critical`,
- `diagnosis` - short sentence summarising the likely cause,
- `advice` - short, actionable follow-up recommendation.

Example:

```python
{
    "id": "battery_issue",
    "conditions": {
        "engine_cranks": False,
        "dashboard_lights_bright": False,
    },
    "system": "battery_charging",
    "severity": "high",
    "diagnosis": "Likely battery or battery connection problem.",
    "advice": "Do not attempt to keep starting the car. Check battery terminals and call roadside assistance or a garage.",
}
```

Across all modules, the system currently contains on the order of 80-100 knowledge elements (symptoms and rules combined), covering common scenarios in starting, braking, cooling, steering, suspension, transmission, electrical and engine management.

### Aggregation

The aggregator in `code/knowledge_base/__init__.py` collects all symptom and rule lists from the subsystem modules and builds deduplicated `SYMPTOMS` and `RULES` lists that are used by the inference engine:

```python
SYMPTOMS = []
_seen_symptom_ids = set()
for group in SYMPTOM_SOURCES:
    for symptom in group:
        symptom_id = symptom["id"]
        if symptom_id not in _seen_symptom_ids:
            SYMPTOMS.append(symptom)
            _seen_symptom_ids.add(symptom_id)
```

The same pattern is used for `RULES`, ensuring no duplicate ids across files.

## Inference

The inference engine treats user answers as observed facts and performs simple data-driven matching, similar to forward chaining:

1. The system iterates through all symptoms in `SYMPTOMS` and asks their questions.
2. Answers are stored as a mapping from symptom id to:
   - `True` for `yes`,
   - `False` for `no`,
   - `None` for skipped/unknown.
3. A rule is considered a match if all of its conditions are satisfied by the observed answers. Unknown answers never cause a rule to fire or be rejected.
4. All matching rules are collected and typically sorted by severity (critical issues first) and by subsystem before being shown to the user.

This behaviour corresponds to a simple forward-style inference: the system starts from user-provided facts and derives all rules whose conditions fit those facts.

## Files

- `code/main.py` - interactive command-line dialogue and printing of diagnoses.
- `code/inference.py` - inference logic for matching answers to rules.
- `code/knowledge_base/__init__.py` - aggregated symptom and rule lists.
- `code/knowledge_base/*.py` - subsystem-specific knowledge modules.
- `requirements.txt` - Python dependencies (currently empty; the standard library is sufficient for this version).

## Limitations and future work

Current limitations:

- The rule base covers only a subset of all possible car faults and focuses on common, generic scenarios.
- The question order is fixed and not yet adaptive to previous answers.
- There is no probabilistic reasoning or ranking beyond simple severity ordering.
- There is no explicit explanation component that shows which rules fired and why.

Planned improvements:

- Extend the knowledge base with more detailed patterns from additional expert interviews.
- Introduce adaptive questioning that only asks questions relevant to still-possible diagnoses.
- Make severity and advice more fine-grained (e.g. explicit safety levels).
- Add automated tests for scenarios and rule coverage.
- Explore a graphical or web-based front-end that uses the same knowledge base and inference engine.

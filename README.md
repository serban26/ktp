# Car Diagnosis Helper – Knowledge-Based Car Troubleshooter

## Overview

Car Diagnosis Helper is a small but complete knowledge-based system that helps car owners reason about simple car problems based on observable symptoms. The system asks a structured series of questions and uses explicit rules to suggest likely causes and possible next steps.

The goal is not to replace a professional mechanic, but to support car owners in:

- deciding whether it is likely safe to keep driving, and  
- having a clearer description of the problem when contacting a garage.

The core knowledge comes from an experienced car mechanic and is stored in a **modular JSON knowledge base**. Each car subsystem (brakes, cooling, ignition, fuel, wheels, steering, etc.) has its own JSON file with symptoms and rules, which are aggregated into one unified knowledge base for inference.

Across all subsystems, the system currently contains a little over 100 knowledge elements (symptoms + rules), which is within the guideline for this project.

## Running the system

Requirements:

- Python 3.10+ (we tested with Python 3.13.2)
- No external dependencies (standard library only)

Steps:

1. From the project root, run:

   ```bash
   python code/main.py
   ```

2. Answer the questions with `yes`, `no`, or press `Enter` to skip if you are unsure.
3. At the end, the system will display one or more possible issues and suggested next steps.

## Project structure

All source code lives in the `code/` directory:

- `code/main.py` – entry point that starts an interactive diagnosis session in the console.
- `code/inference.py` – inference engine that matches user answers to rules and prints diagnoses.
- `code/knowledge_base.py` – loader and aggregator that reads the JSON knowledge base and exposes:
  - `CAR_SYSTEMS` – list of car subsystems (battery/charging, brakes, cooling, etc.).
  - `SYMPTOMS` – flat list of all symptom objects from all JSON files.
  - `RULES` – flat list of all rule objects from all JSON files.
- `code/kb_data/` – JSON knowledge base:
  - `general.json` – subsystem list (`systems`) and general symptoms/rules that cut across subsystems.
  - `brakes.json` – brake symptoms and rules.
  - `climate_ac.json` – climate control and A/C symptoms and rules.
  - `cooling.json` – engine cooling symptoms and rules.
  - `electrical_lighting.json` – basic electrical and lighting symptoms and rules.
  - `engine_fuel.json` – fuel delivery and injection symptoms and rules.
  - `engine_ignition.json` – ignition-related symptoms and rules.
  - `engine_mechanical.json` – mechanical engine symptoms and rules.
  - `steering_suspension.json` – steering and suspension symptoms and rules.
  - `transmission.json` – transmission and clutch symptoms and rules.
  - `wheels.json` – wheel and tyre symptoms and rules.
- `requirements.txt` – Python dependencies file (currently empty; included to satisfy project requirements).

The JSON files contain only declarative knowledge (symptoms, rules, subsystem identifiers). All procedural code for asking questions and performing inference lives in `main.py`, `inference.py`, and `knowledge_base.py`.

## Knowledge representation

### Car systems

Subsystem identifiers and human-readable names are stored in `kb_data/general.json` under the key `systems`. For example:

```json
{
  "systems": [
    { "id": "battery_charging", "name": "Battery and charging system" },
    { "id": "starting_system", "name": "Starting system" },
    { "id": "brake_hydraulic", "name": "Brake hydraulic system" }
  ]
}
```

These identifiers are referenced by rules so that each diagnosis is linked to the relevant part of the car.

### Symptoms

Symptoms are stored in each JSON file as small objects with an `id` and a natural-language `question`. Example:

```json
{
  "id": "engine_cranks",
  "question": "When you try to start the car, does the engine crank or turn over? (yes/no)"
}
```

Each symptom is designed to be observable without tools by an average driver (starting behaviour, lights, noises, smells, vibrations, performance changes).

### Rules

Rules are stored in JSON as objects with:

- `id` – unique rule identifier,
- `conditions` – mapping from symptom ids to expected boolean values (`true` / `false`),
- `system` – affected car subsystem identifier (from `systems` in `general.json`),
- `diagnosis` – short sentence summarising the likely cause,
- `advice` – short, actionable follow-up recommendation.

Example:

```json
{
  "id": "battery_issue",
  "conditions": {
    "engine_cranks": false,
    "dashboard_lights_bright": false
  },
  "system": "battery_charging",
  "diagnosis": "Likely battery or battery connection problem.",
  "advice": "Do not keep trying to start the car. Check battery terminals and call roadside assistance or a garage."
}
```

Each subsystem file adds its own set of symptoms and rules; the aggregator combines them into a single view for the inference engine.

## Aggregation and inference

### Loading and aggregation

`code/knowledge_base.py` reads all JSON files in `kb_data/`. It:

- loads `systems`, `symptoms`, and `rules` from `general.json`,
- loads `symptoms` and `rules` from each of the subsystem files,
- merges them into global `SYMPTOMS` and `RULES` lists,
- removes duplicates based on `id` so that each symptom and rule appears only once.

This loader does not contain any hard-coded rules itself; all knowledge is read from the JSON files.

### Asking questions and collecting observations

`code/inference.py` iterates over all entries in `SYMPTOMS` and asks the user each question in order. Answers are stored in a dictionary:

- `True` for “yes”,
- `False` for “no”,
- `None` for skipped/unknown (when the user presses Enter).

### Rule matching

For each rule in `RULES`, the inference engine checks whether the rule’s conditions are compatible with the observed answers:

- If a condition refers to a symptom the user **skipped** (`None`), that condition is ignored for that rule.
- If a condition refers to a symptom that the user answered, and the answer contradicts the expected value, the rule does **not** match.
- If at least one condition is supported by an explicit answer and none of the answered conditions contradict the rule, the rule is considered a match and its diagnosis is shown.

In other words, skipped questions do not directly influence the result: only questions that the user actually answered are used to accept or reject rules.

### Result presentation

All rules that match the user’s answers are collected and shown back to the user in a simple list. For each match, the system prints:

- the `diagnosis` (likely cause),
- the `advice` (concrete next step or safety recommendation).

## Limitations and future work

Current limitations:

- The rule base covers only a subset of all possible car faults and focuses on common, generic scenarios.
- The question order is fixed and not yet adaptive to previous answers.
- There is no explicit explanation component that shows which exact rules fired and why.
- Skipping many questions may prevent some rules from matching, because at least one condition must be supported by an explicit answer.

Planned improvements:

- Extend the knowledge base with more detailed patterns from additional expert interviews.
- Introduce adaptive questioning that only asks questions relevant to still-possible diagnoses.
- Explore a graphical or web-based front-end that uses the same JSON knowledge base and inference engine.

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
- Streamlit (see `requirements.txt`)

Steps:

1. Install dependencies from the project root:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit app from the project root:

   ```bash
   streamlit run code/main.py
   ```

3. Answer the questions using the UI buttons (`Yes`, `No`, or `Skip`).
4. At the end, the system will display one or more possible issues and suggested next steps.

## Project structure

All source code lives in the `code/` directory:

- `code/main.py` – entry point that starts the Streamlit web app and manages the diagnosis session state.
- `code/inference.py` – inference logic that filters/ranks rules and selects the next question based on remaining candidate rules.
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
- `requirements.txt` – Python dependencies file (includes Streamlit to ensure reproducibility).

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
- `advice` – short, actionable follow-up recommendation,
- `severity` – a coarse urgency label (`low`, `medium`, `high`) used for result presentation.

Example:

```json
{
  "id": "battery_issue",
  "conditions": {
    "engine_cranks": false,
    "dashboard_lights_bright": false
  },
  "system": "battery_charging",
  "severity": "high",
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

The Streamlit UI in `code/main.py` manages a single diagnosis session. It asks questions one by one and stores answers in a dictionary:

- `True` for “yes”,
- `False` for “no”,
- `None` for skipped/unknown.

Unlike a console loop, the Streamlit app stores the session state across UI interactions so the user can answer comfortably without typing.

### Candidate filtering and next-question selection

The inference logic maintains a set of rules that are still compatible with the answers given so far:

- If an answered symptom contradicts the expected value of a rule condition, that rule is removed from the candidate set.
- Skipped symptoms do not remove rules.

To avoid asking every possible question, the next question is selected from symptoms that appear in the remaining candidate rules and have not been asked yet. A simple heuristic is used: choose a symptom that appears most frequently in remaining candidates, because it tends to eliminate many rules quickly.

This keeps the dialogue relatively short while still allowing deeper paths where multiple diagnoses must be ruled out.

### Rule matching and results

After questioning ends (or when there are no remaining informative questions), the system ranks candidate rules and displays the best matching ones. For each match, it shows:

- the `diagnosis` (likely cause),
- the `system` (subsystem name),
- the `severity` label,
- the `advice` (concrete next step or safety recommendation).

## Limitations and future work

Current limitations:

- The rule base covers only a subset of all possible car faults and focuses on common, generic scenarios.
- Some faults are ambiguous without tools (OBD fault codes, pressure tests, etc.), so the system reports plausible candidates rather than a single definitive answer.
- The question selection heuristic is simple; it is effective in practice but not guaranteed optimal.
- Skipping many questions reduces discrimination power, because fewer rule conditions can be supported.

Planned improvements:

- Extend the knowledge base with more detailed patterns from additional expert interviews.
- Improve adaptive questioning using a more explicit information-gain style criterion.
- Add an explanation component that shows which exact answers supported each diagnosis.
- Add more scenario-based validation with the expert mechanic and a regression test set.

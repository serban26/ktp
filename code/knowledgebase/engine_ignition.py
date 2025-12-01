SYMPTOMS_ENGINE_IGNITION = [
    {
        "id": "misfire_at_idle",
        "question": "Does the engine feel like it occasionally misses a beat while idling? (yes/no)",
    },
    {
        "id": "misfire_wet_weather",
        "question": "Are misfires or hesitation worse in wet or very humid weather? (yes/no)",
    },
    {
        "id": "backfire_intake",
        "question": "Have you noticed popping or backfiring noises from the intake or air filter area? (yes/no)",
    },
    {
        "id": "engine_cranks_no_start",
        "question": "Does the engine crank strongly but fail to start at all? (yes/no)",
    },
]

RULES_ENGINE_IGNITION = [
    {
        "id": "ignition_misfire_idle",
        "conditions": {
            "misfire_at_idle": True,
            "warning_check_engine": True,
        },
        "system": "engine_ignition",
        "severity": "medium",
        "diagnosis": "Misfire at idle with a check engine light often points to ignition coil or spark plug issues.",
        "advice": "Continued misfiring can damage the catalytic converter. Have ignition components and fault codes checked.",
    },
    {
        "id": "ignition_leads_damp",
        "conditions": {
            "misfire_wet_weather": True,
        },
        "system": "engine_ignition",
        "severity": "low",
        "diagnosis": "Misfires that are worse in wet weather suggest moisture-sensitive ignition leads or coil packs.",
        "advice": "Inspect ignition leads and coils for cracks and moisture paths and consider replacement.",
    },
    {
        "id": "intake_backfire_timing",
        "conditions": {
            "backfire_intake": True,
        },
        "system": "engine_ignition",
        "severity": "medium",
        "diagnosis": "Backfiring through the intake can be caused by incorrect ignition timing or lean misfire.",
        "advice": "Driving should be limited until ignition timing and air–fuel mixture have been checked.",
    },
    {
        "id": "no_start_possible_ignition",
        "conditions": {
            "engine_cranks_no_start": True,
            "smell_fuel_engine_bay": True,
        },
        "system": "engine_ignition",
        "severity": "high",
        "diagnosis": "Strong fuel smell with cranking but no start suggests lack of spark rather than fuel.",
        "advice": "Have the ignition system checked for spark at the plugs and possible crankshaft or camshaft sensor faults.",
    },
]

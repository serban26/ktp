SYMPTOMS_COOLING = [
    {
        "id": "overheating_gauge_high",
        "question": "Is the temperature gauge higher than normal or in the red zone? (yes/no)",
    },
    {
        "id": "temp_fluctuates",
        "question": "Does the temperature gauge move up and down more than usual while driving? (yes/no)",
    },
    {
        "id": "coolant_loss_visible",
        "question": "Have you noticed coolant loss, wet spots, or dried coolant residue around the engine bay? (yes/no)",
    },
    {
        "id": "heater_not_warm",
        "question": "When the engine is warm, does the cabin heater blow only cold or slightly warm air? (yes/no)",
    },
    {
        "id": "sweet_smell",
        "question": "Do you notice a sweet smell inside or around the car, especially after driving? (yes/no)",
    },
]

RULES_COOLING = [
    {
        "id": "coolant_leak",
        "conditions": {
            "overheating_gauge_high": True,
            "sweet_smell": True,
        },
        "system": "cooling_system",
        "severity": "critical",
        "diagnosis": "Possible coolant leak or overheating problem.",
        "advice": "Do not continue driving with an overheating engine. Stop safely, allow the engine to cool, and contact roadside assistance or a garage.",
    },
    {
        "id": "thermostat_stuck",
        "conditions": {
            "temp_fluctuates": True,
            "overheating_gauge_high": False,
        },
        "system": "cooling_system",
        "severity": "medium",
        "diagnosis": "Fluctuating temperature without constant overheating can indicate a thermostat issue.",
        "advice": "Have the cooling system and thermostat checked to avoid future overheating problems.",
    },
    {
        "id": "low_coolant_heater",
        "conditions": {
            "heater_not_warm": True,
            "coolant_loss_visible": True,
            "overheating_gauge_high": False,
        },
        "system": "cooling_system",
        "severity": "high",
        "diagnosis": "Poor cabin heat with coolant loss suggests low coolant level or air in the system.",
        "advice": "Driving with low coolant can quickly lead to overheating. Have the system checked and refilled.",
    },
    {
        "id": "severe_overheating",
        "conditions": {
            "overheating_gauge_high": True,
            "coolant_loss_visible": True,
        },
        "system": "cooling_system",
        "severity": "critical",
        "diagnosis": "Engine is overheating and coolant loss is visible.",
        "advice": "Stop driving immediately, switch off the engine, and arrange for the car to be inspected before driving again.",
    },
]

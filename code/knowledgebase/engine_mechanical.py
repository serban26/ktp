SYMPTOMS_ENGINE_MECHANICAL = [
    {
        "id": "knocking_noise_under_load",
        "question": "Do you hear a knocking or banging noise from the engine when accelerating or driving uphill? (yes/no)",
    },
    {
        "id": "low_oil_pressure_light",
        "question": "Does the oil pressure or oil warning light come on while driving? (yes/no)",
    },
    {
        "id": "blue_smoke_exhaust",
        "question": "Do you notice blue or bluish smoke from the exhaust, especially when accelerating? (yes/no)",
    },
    {
        "id": "tapping_noise_cold_start",
        "question": "Do you hear a light tapping or ticking noise from the engine when it is cold that reduces when warm? (yes/no)",
    },
]

RULES_ENGINE_MECHANICAL = [
    {
        "id": "low_oil_pressure_critical",
        "conditions": {
            "low_oil_pressure_light": True,
        },
        "system": "engine_mechanical",
        "severity": "critical",
        "diagnosis": "Low oil pressure warning indicates a serious lubrication problem.",
        "advice": "Stop the engine as soon as it is safe to do so and check the oil level. Do not continue driving with low oil pressure.",
    },
    {
        "id": "rod_knock_engine",
        "conditions": {
            "knocking_noise_under_load": True,
            "low_oil_pressure_light": False,
        },
        "system": "engine_mechanical",
        "severity": "high",
        "diagnosis": "Knocking under load without low oil pressure can indicate worn engine bearings or detonation.",
        "advice": "Avoid high loads and have the engine inspected. Long-term driving can cause major engine damage.",
    },
    {
        "id": "valve_tappet_noise",
        "conditions": {
            "tapping_noise_cold_start": True,
        },
        "system": "engine_mechanical",
        "severity": "low",
        "diagnosis": "Tapping noise on cold start that improves when warm can be caused by valve lifters or clearances.",
        "advice": "Mention this symptom during the next service so that valve clearances and oil quality can be checked.",
    },
    {
        "id": "oil_burning",
        "conditions": {
            "blue_smoke_exhaust": True,
        },
        "system": "engine_mechanical",
        "severity": "medium",
        "diagnosis": "Blue exhaust smoke usually indicates that the engine is burning oil.",
        "advice": "Monitor oil level frequently and have compression or leak-down tests performed to locate worn components.",
    },
]

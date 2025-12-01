SYMPTOMS_TRANSMISSION = [
    {
        "id": "engine_revs_no_accel",
        "question": "When you accelerate, do the engine revs rise but the car does not speed up accordingly? (yes/no)",
    },
    {
        "id": "difficulty_engaging_gears",
        "question": "Is it difficult to engage gears or do they sometimes refuse to go in? (yes/no)",
    },
    {
        "id": "grinding_when_shifting",
        "question": "Do you hear grinding noises when changing gears? (yes/no)",
    },
    {
        "id": "clutch_pedal_high_bite",
        "question": "Does the clutch engage very high up in the pedal travel? (yes/no)",
    },
]

RULES_TRANSMISSION = [
    {
        "id": "clutch_slip",
        "conditions": {
            "engine_revs_no_accel": True,
            "difficulty_engaging_gears": False,
        },
        "system": "transmission_clutch",
        "severity": "medium",
        "diagnosis": "Rising engine speed without matching acceleration suggests clutch slip.",
        "advice": "Avoid hard acceleration and have the clutch inspected before it fails completely.",
    },
    {
        "id": "clutch_worn_high_bite",
        "conditions": {
            "clutch_pedal_high_bite": True,
        },
        "system": "transmission_clutch",
        "severity": "medium",
        "diagnosis": "A very high clutch biting point usually indicates a worn clutch.",
        "advice": "Plan for clutch replacement, especially if there are also signs of slip or noise.",
    },
    {
        "id": "gearbox_synchroniser_wear",
        "conditions": {
            "grinding_when_shifting": True,
            "difficulty_engaging_gears": True,
        },
        "system": "transmission_clutch",
        "severity": "medium",
        "diagnosis": "Grinding and difficulty engaging gears suggest worn gearbox synchronisers or clutch drag.",
        "advice": "Have clutch adjustment and gearbox oil checked; further diagnosis may be required.",
    },
    {
        "id": "clutch_drag",
        "conditions": {
            "difficulty_engaging_gears": True,
            "engine_revs_no_accel": False,
        },
        "system": "transmission_clutch",
        "severity": "medium",
        "diagnosis": "Difficulty engaging gears without slip can be caused by incomplete clutch disengagement.",
        "advice": "Clutch hydraulics or cable may need adjustment or repair to prevent gearbox damage.",
    },
]

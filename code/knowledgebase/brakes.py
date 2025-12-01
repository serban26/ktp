SYMPTOMS_BRAKES = [
    {
        "id": "strange_brake_noise",
        "question": "Do you hear a high-pitched squealing or grinding noise when braking? (yes/no)",
    },
    {
        "id": "car_pulls_braking",
        "question": "Does the car pull strongly to one side when braking? (yes/no)",
    },
    {
        "id": "brake_warning_light",
        "question": "Is a brake warning light on in the dashboard? (yes/no)",
    },
    {
        "id": "brake_pedal_spongy",
        "question": "Does the brake pedal feel soft or spongy and travel further than usual? (yes/no)",
    },
    {
        "id": "brake_pedal_hard",
        "question": "Does the brake pedal feel unusually hard and require a lot of force? (yes/no)",
    },
]

RULES_BRAKES = [
    {
        "id": "brake_pads_worn",
        "conditions": {
            "strange_brake_noise": True,
        },
        "system": "brake_mechanical",
        "severity": "high",
        "diagnosis": "Brake pads or discs may be worn.",
        "advice": "Continuous squealing or grinding when braking suggests worn pads or discs. Reduce driving and book a brake inspection soon.",
    },
    {
        "id": "brake_imbalance",
        "conditions": {
            "car_pulls_braking": True,
        },
        "system": "brake_hydraulic",
        "severity": "high",
        "diagnosis": "Possible brake imbalance or sticking brake on one side.",
        "advice": "Pulling to one side while braking can be dangerous. Avoid high-speed driving and visit a garage as soon as possible.",
    },
    {
        "id": "brake_fluid_or_leak",
        "conditions": {
            "brake_warning_light": True,
        },
        "system": "brake_hydraulic",
        "severity": "critical",
        "diagnosis": "Possible low brake fluid level or brake system leak.",
        "advice": "A brake warning light can indicate a serious fault. Do not continue driving until the brake system has been inspected.",
    },
    {
        "id": "air_in_brake_lines",
        "conditions": {
            "brake_pedal_spongy": True,
        },
        "system": "brake_hydraulic",
        "severity": "high",
        "diagnosis": "Spongy brake pedal may indicate air in the brake lines or fluid issues.",
        "advice": "Reduced brake firmness can greatly increase stopping distance. Have the brake system bled and checked as soon as possible.",
    },
    {
        "id": "brake_booster_issue",
        "conditions": {
            "brake_pedal_hard": True,
            "engine_runs_rough_idle": True,
        },
        "system": "brake_hydraulic",
        "severity": "high",
        "diagnosis": "Hard brake pedal together with rough idle can indicate a brake booster or vacuum leak problem.",
        "advice": "A failing brake booster affects braking effort and engine running. Avoid driving in heavy traffic and have the system inspected.",
    },
]

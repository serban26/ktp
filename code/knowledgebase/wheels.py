SYMPTOMS_WHEELS = [
    {
        "id": "vibration_high_speed",
        "question": "Do you feel vibration in the steering wheel at higher speeds (above 80 km/h)? (yes/no)",
    },
    {
        "id": "vibration_low_speed",
        "question": "Do you feel vibration at low speeds (below 50 km/h)? (yes/no)",
    },
    {
        "id": "steering_wobble_turning",
        "question": "Does the steering wheel wobble noticeably when turning or cornering? (yes/no)",
    },
    {
        "id": "tyre_wear_inner_outer",
        "question": "Do the tyres show more wear on the inner or outer edge compared to the centre? (yes/no)",
    },
]

RULES_WHEELS = [
    {
        "id": "wheel_balance_issue",
        "conditions": {
            "vibration_high_speed": True,
        },
        "system": "wheel_tyre_system",
        "severity": "low",
        "diagnosis": "Likely wheel balance or alignment issue.",
        "advice": "Vibration at higher speeds often comes from wheel balance or alignment. Driving is usually still possible, but have it checked to avoid uneven tyre wear.",
    },
    {
        "id": "bent_wheel_or_tyre_defect",
        "conditions": {
            "vibration_low_speed": True,
            "vibration_high_speed": False,
        },
        "system": "wheel_tyre_system",
        "severity": "medium",
        "diagnosis": "Vibration mainly at low speed can indicate a bent wheel or tyre defect.",
        "advice": "Have the wheels and tyres inspected for damage, especially after hitting potholes or kerbs.",
    },
    {
        "id": "loose_suspension_component",
        "conditions": {
            "steering_wobble_turning": True,
        },
        "system": "steering_suspension",
        "severity": "high",
        "diagnosis": "Steering wobble when turning can point to worn or loose suspension or steering components.",
        "advice": "Have the suspension and steering checked soon to avoid worsening wear or safety issues.",
    },
    {
        "id": "wheel_alignment_issue",
        "conditions": {
            "tyre_wear_inner_outer": True,
        },
        "system": "wheel_tyre_system",
        "severity": "medium",
        "diagnosis": "Uneven tyre edge wear usually indicates incorrect wheel alignment or suspension geometry.",
        "advice": "Book a wheel alignment check to prevent premature tyre wear and possible pulling while driving.",
    },
]

SYMPTOMS = [
    {
        "id": "engine_cranks",
        "question": "When you try to start the car, does the engine crank or turn over? (yes/no)"
    },
    {
        "id": "dashboard_lights_bright",
        "question": "When the ignition is on, are the dashboard lights bright and normal? (yes/no)"
    },
    {
        "id": "warning_check_engine",
        "question": "Is the check engine warning light on while driving? (yes/no)"
    },
    {
        "id": "strange_brake_noise",
        "question": "Do you hear a high-pitched squealing or grinding noise when braking? (yes/no)"
    },
    {
        "id": "car_pulls_braking",
        "question": "Does the car pull strongly to one side when braking? (yes/no)"
    },
    {
        "id": "overheating_gauge_high",
        "question": "Is the temperature gauge higher than normal or in the red zone? (yes/no)"
    },
    {
        "id": "sweet_smell",
        "question": "Do you notice a sweet smell inside or around the car, especially after driving? (yes/no)"
    },
    {
        "id": "vibration_high_speed",
        "question": "Do you feel vibration in the steering wheel at higher speeds (above 80 km/h)? (yes/no)"
    }
]

RULES = [
    {
        "id": "battery_issue",
        "conditions": {
            "engine_cranks": False,
            "dashboard_lights_bright": False
        },
        "diagnosis": "Likely battery or battery connection problem.",
        "advice": "Do not attempt to keep starting the car. Check battery terminals and call roadside assistance or a garage."
    },
    {
        "id": "starter_issue",
        "conditions": {
            "engine_cranks": False,
            "dashboard_lights_bright": True
        },
        "diagnosis": "Possible starter motor or ignition circuit issue.",
        "advice": "The electrical system appears to have power but the engine does not crank. It is safer to have the car inspected by a mechanic."
    },
    {
        "id": "engine_running_with_check_light",
        "conditions": {
            "engine_cranks": True,
            "warning_check_engine": True
        },
        "diagnosis": "Engine control system has detected a fault.",
        "advice": "The car may still be drivable, but avoid hard acceleration and have the fault code read at a garage as soon as possible."
    },
    {
        "id": "brake_pads_worn",
        "conditions": {
            "strange_brake_noise": True
        },
        "diagnosis": "Brake pads or discs may be worn.",
        "advice": "Continuous squealing or grinding when braking suggests worn pads or discs. Reduce driving and book a brake inspection soon."
    },
    {
        "id": "brake_imbalance",
        "conditions": {
            "car_pulls_braking": True
        },
        "diagnosis": "Possible brake imbalance or sticking brake on one side.",
        "advice": "Pulling to one side while braking can be dangerous. Avoid high-speed driving and visit a garage as soon as possible."
    },
    {
        "id": "coolant_leak",
        "conditions": {
            "overheating_gauge_high": True,
            "sweet_smell": True
        },
        "diagnosis": "Possible coolant leak or overheating problem.",
        "advice": "Do not continue driving with an overheating engine. Stop safely, allow the engine to cool, and contact roadside assistance or a garage."
    },
    {
        "id": "wheel_balance_issue",
        "conditions": {
            "vibration_high_speed": True
        },
        "diagnosis": "Likely wheel balance or alignment issue.",
        "advice": "Vibration at higher speeds often comes from wheel balance or alignment. Driving is usually still possible, but have it checked to avoid uneven tyre wear."
    }
]

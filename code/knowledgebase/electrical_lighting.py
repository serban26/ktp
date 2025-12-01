SYMPTOMS_ELECTRICAL_LIGHTING = [
    {
        "id": "headlights_dim_idle",
        "question": "Do the headlights become noticeably dimmer when the engine is idling? (yes/no)",
    },
    {
        "id": "indicators_flash_fast",
        "question": "Do the turn indicators flash faster than normal on one side? (yes/no)",
    },
    {
        "id": "interior_lights_flicker",
        "question": "Do interior lights flicker or vary in brightness while driving? (yes/no)",
    },
    {
        "id": "single_light_not_working",
        "question": "Is there a single headlight or tail light that does not work while others do? (yes/no)",
    },
]

RULES_ELECTRICAL_LIGHTING = [
    {
        "id": "alternator_weak_lighting",
        "conditions": {
            "headlights_dim_idle": True,
            "engine_cranks": True,
        },
        "system": "body_lighting_electrical",
        "severity": "medium",
        "diagnosis": "Headlights that dim at idle can indicate a weak alternator or poor charging at low speed.",
        "advice": "Have the charging system output checked, especially if combined with battery warnings.",
    },
    {
        "id": "indicator_bulb_out",
        "conditions": {
            "indicators_flash_fast": True,
        },
        "system": "body_lighting_electrical",
        "severity": "low",
        "diagnosis": "Fast flashing on one side usually indicates a failed indicator bulb.",
        "advice": "Check the bulbs on the affected side and replace any that are not working.",
    },
    {
        "id": "poor_battery_connection_lights",
        "conditions": {
            "interior_lights_flicker": True,
            "dashboard_lights_bright": False,
        },
        "system": "body_lighting_electrical",
        "severity": "medium",
        "diagnosis": "Flickering lights with weak dash illumination can be caused by poor battery or earth connections.",
        "advice": "Have the main battery and earth connections cleaned and tightened.",
    },
    {
        "id": "single_bulb_failure",
        "conditions": {
            "single_light_not_working": True,
        },
        "system": "body_lighting_electrical",
        "severity": "low",
        "diagnosis": "A single light out while others work normally is usually just a failed bulb.",
        "advice": "Replace the failed bulb and check that the light operates again.",
    },
]

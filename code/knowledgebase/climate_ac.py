SYMPTOMS_CLIMATE_AC = [
    {
        "id": "ac_not_cold",
        "question": "When the air conditioning is on, does the air remain only slightly cool or not cold at all? (yes/no)",
    },
    {
        "id": "ac_smell_musty",
        "question": "Does the air from the vents have a musty or mouldy smell when the AC is used? (yes/no)",
    },
    {
        "id": "windows_fog_easily",
        "question": "Do the windows fog up easily on the inside, even with ventilation on? (yes/no)",
    },
    {
        "id": "ac_noise_on",
        "question": "Do you hear unusual noises when the AC or fan is switched on? (yes/no)",
    },
]

RULES_CLIMATE_AC = [
    {
        "id": "low_refrigerant",
        "conditions": {
            "ac_not_cold": True,
            "ac_noise_on": True,
        },
        "system": "climate_ac",
        "severity": "medium",
        "diagnosis": "Poor cooling with noises when AC is on can indicate low refrigerant or compressor issues.",
        "advice": "Have the AC system checked for leaks and correct refrigerant level.",
    },
    {
        "id": "cabin_filter_dirty",
        "conditions": {
            "ac_smell_musty": True,
            "windows_fog_easily": True,
        },
        "system": "climate_ac",
        "severity": "low",
        "diagnosis": "Musty smell and easy fogging often point to a dirty cabin filter or moisture in the ventilation system.",
        "advice": "Replacing the cabin filter and cleaning the vents can improve smell and visibility.",
    },
    {
        "id": "ac_not_used_regularly",
        "conditions": {
            "ac_smell_musty": True,
            "ac_not_cold": False,
        },
        "system": "climate_ac",
        "severity": "low",
        "diagnosis": "Musty smell with normal cooling can be caused by condensation and bacterial growth on the evaporator.",
        "advice": "Running the AC regularly and using an AC cleaner product can help reduce odours.",
    },
    {
        "id": "blower_or_fan_issue",
        "conditions": {
            "ac_noise_on": True,
            "ac_not_cold": False,
        },
        "system": "climate_ac",
        "severity": "low",
        "diagnosis": "Noises when the fan runs but cooling is normal can indicate leaves or wear in the blower fan.",
        "advice": "Have the blower motor and fan housing inspected, especially if noises get worse over time.",
    },
]

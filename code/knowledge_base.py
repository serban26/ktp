from knowledgebase.general import CAR_SYSTEMS, SYMPTOMS_GENERAL, RULES_GENERAL
from knowledgebase.brakes import SYMPTOMS_BRAKES, RULES_BRAKES
from knowledgebase.climate_ac import SYMPTOMS_CLIMATE_AC, RULES_CLIMATE_AC
from knowledgebase.cooling import SYMPTOMS_COOLING, RULES_COOLING
from knowledgebase.electrical_lighting import SYMPTOMS_ELECTRICAL_LIGHTING, RULES_ELECTRICAL_LIGHTING
from knowledgebase.engine_fuel import SYMPTOMS_ENGINE_FUEL, RULES_ENGINE_FUEL
from knowledgebase.engine_ignition import SYMPTOMS_ENGINE_IGNITION, RULES_ENGINE_IGNITION
from knowledgebase.engine_mechanical import SYMPTOMS_ENGINE_MECHANICAL, RULES_ENGINE_MECHANICAL
from knowledgebase.steering_suspension import SYMPTOMS_STEERING_SUSPENSION, RULES_STEERING_SUSPENSION
from knowledgebase.transmission import SYMPTOMS_TRANSMISSION, RULES_TRANSMISSION
from knowledgebase.wheels import SYMPTOMS_WHEELS, RULES_WHEELS


SYMPTOM_SOURCES = [
    SYMPTOMS_GENERAL,
    SYMPTOMS_ENGINE_IGNITION,
    SYMPTOMS_BRAKES,
    SYMPTOMS_CLIMATE_AC,
    SYMPTOMS_COOLING,
    SYMPTOMS_ELECTRICAL_LIGHTING,
    SYMPTOMS_ENGINE_FUEL,
    SYMPTOMS_ENGINE_MECHANICAL,
    SYMPTOMS_STEERING_SUSPENSION,
    SYMPTOMS_TRANSMISSION,
    SYMPTOMS_WHEELS,
]


RULE_SOURCES = [
    RULES_GENERAL,
    RULES_ENGINE_IGNITION,
    RULES_BRAKES,
    RULES_CLIMATE_AC,
    RULES_COOLING,
    RULES_ELECTRICAL_LIGHTING,
    RULES_ENGINE_FUEL,
    RULES_ENGINE_MECHANICAL,
    RULES_STEERING_SUSPENSION,
    RULES_TRANSMISSION,
    RULES_WHEELS,
]


SYMPTOMS = []
_seen_symptom_ids = set()
for group in SYMPTOM_SOURCES:
    for symptom in group:
        symptom_id = symptom["id"]
        if symptom_id not in _seen_symptom_ids:
            SYMPTOMS.append(symptom)
            _seen_symptom_ids.add(symptom_id)


RULES = []
_seen_rule_ids = set()
for group in RULE_SOURCES:
    for rule in group:
        rule_id = rule["id"]
        if rule_id not in _seen_rule_ids:
            RULES.append(rule)
            _seen_rule_ids.add(rule_id)

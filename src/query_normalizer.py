"""
Filename: query_normalizer.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    Rule-based synonym expansion system that converts natural
    language user queries into technical terminology found in
    automotive manuals. Improves recall for IR tasks.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import re

# Rule-based synonym expansion dictionary
EXPANSION_MAP = {
    # VIBRATIONS / SHAKING
    "shake": ["vibration", "shudder", "judder", "wobble"],
    "shaking": ["vibration", "shudder", "judder"],
    "vibrate": ["vibration", "shudder", "floor vibration"],
    "vibration": ["shake", "shudder", "judder"],

    # BRAKING / ROTOR ISSUES
    "brake": ["braking", "rotor", "pad wear", "rotor thickness variation", "runout"],
    "braking": ["caliper", "pads", "rotor runout"],
    "brake noise": ["squeal", "grind", "pad wear indicator"],

    # ENGINE IDLE / STALL / MISFIRE
    "stall": ["engine stall", "idle speed", "idle mixture", "stalling"],
    "idling": ["idle speed", "idle mixture", "rough idle"],
    "misfire": ["ignition coil", "spark plug", "fuel mixture", "rough idle"],
    "rough idle": ["egr passage", "fuel trim", "idle control"],
    "hesitate": ["poor acceleration", "misfire", "throttle response"],
    "acceleration": ["throttle", "fuel delivery", "hesitation"],
    "jerk": ["hesitation", "misfire"],

    # FUEL & EXHAUST SMELLS
    "fuel smell": ["evap leak", "fuel vapor", "charcoal canister", "purge valve"],
    "poor fuel": ["fuel economy", "fuel trim", "evap leak"],
    "exhaust smell": ["rich mixture", "oxygen sensor", "air fuel ratio sensor"],

    # OVERHEATING
    "overheat": ["coolant", "radiator", "thermostat", "water pump", "cooling system"],
    "overheating": ["coolant level", "coolant leak"],

    # DRIVE SHAFT / NOISE / CLUNK
    "clunk": ["drive shaft", "cv joint", "suspected area", "driveline"],
    "noise when turning": ["drive shaft", "cv joint", "steering", "front axle"],
    "vibration when accelerating": ["drive shaft", "propeller shaft", "runout"],

    # AIRBAG / SRS SYSTEM
    "airbag": ["srs", "srs lamp", "airbag module", "airbag sensor"],
    "srs": ["airbag", "pretensioner", "srs ecu"],
    "pretensioner": ["seat belt pretensioner", "srs", "squib"],

    # COMMUNICATION / DIAGNOSTIC ERRORS
    "communication error": ["no communication", "bus line", "diagnostic system", "can bus"],
    "no communication": ["can high", "can low", "bus fault", "module offline"],
    "diagnostic": ["obd", "scan tool", "vehicle diagnostic system"],
    "module not responding": ["communication bus", "can fault"],

    # AUDIO / RADIO / ELECTRICAL
    "radio": ["audio unit", "head unit", "entertainment system"],
    "stereo": ["audio unit", "head unit"],
    "speakers not working": ["audio circuit", "radio", "head unit"],

    # STARTING ISSUES
    "won't start": ["no crank", "engine no-start", "starter motor", "battery"],
    "wont start": ["no crank", "starter circuit"],
    "no start": ["starter relay", "ignition switch"],

    # TRANSMISSION / SLIPPING
    "slip": ["transmission slipping", "gear engagement issue"],
    "slipping": ["transmission slip", "gear issue"]
}

def normalize_query(query: str) -> str:
    """
    Convert human phrasing into a more technical IR-friendly query.
    Returns an expanded query string.
    """

    q = query.lower()

    expanded_terms = []

    # Go through each key phrase, add expansions if found
    for key, expansions in EXPANSION_MAP.items():
        if key in q:
            expanded_terms.extend(expansions)

    # Append expanded terms to the original query
    expanded_query = q + " " + " ".join(expanded_terms)

    return expanded_query.strip()

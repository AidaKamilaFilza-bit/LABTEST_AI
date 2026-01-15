# app.py
import json
from typing import List, Dict, Any, Tuple
import operator
import streamlit as st

# ----------------------------
# 1) Rule Engine
# ----------------------------
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

DEFAULT_RULES: List[Dict[str, Any]] = [

    {
        "name": "Windows open → turn AC off",
        "priority": 100,
        "conditions": [
            ["windows_open", "==", True]
        ],
        "action": {
            "mode": "OFF",
            "fan_speed": "LOW",
            "setpoint": None,
            "reason": "Windows are open"
        }
    },

    {
        "name": "No one home → eco mode",
        "priority": 90,
        "conditions": [
            ["occupancy", "==", "EMPTY"],
            ["temperature", ">=", 24]
        ],
        "action": {
            "mode": "ECO",
            "fan_speed": "LOW",
            "setpoint": 27,
            "reason": "Home empty, save energy"
        }
    },

    {
        "name": "Hot & humid (occupied) → strong cooling",
        "priority": 80,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 30],
            ["humidity", ">=", 70]
        ],
        "action": {
            "mode": "COOL",
            "fan_speed": "HIGH",
            "setpoint": 23,
            "reason": "Hot and humid"
        }
    },

    {
        "name": "Hot (occupied) → cool",
        "priority": 70,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 28]
        ],
        "action": {
            "mode": "COOL",
            "fan_speed": "MEDIUM",
            "setpoint": 24,
            "reason": "Temperature high"
        }
    },

    {
        "name": "Slightly warm (occupied) → gentle cool",
        "priority": 60,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 26],
            ["temperature", "<", 28]
        ],
        "action": {
            "mode": "COOL",
            "fan_speed": "LOW",
            "setpoint": 25,
            "reason": "Slightly warm"
        }
    },

    {
        "name": "Night (occupied) → sleep mode",
        "priority": 75,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["time_of_day", "==", "NIGHT"],
            ["temperature", ">=", 26]
        ],
        "action": {
            "mode": "SLEEP",
            "fan_speed": "LOW",
            "setpoint": 26,
            "reason": "Night comfort"
        }
    },

    {
        "name": "Too cold → turn off",
        "priority": 85,
        "conditions": [
            ["temperature", "<=", 22]
        ],
        "action": {
            "mode": "OFF",
            "fan_speed": "LOW",
            "setpoint": None,
            "reason": "Already cold"
        }
    }
]

def evaluate_condition(facts: Dict[str, Any], cond: List[Any]) -> bool:
    field, op, value = cond
    if field not in facts or op not in OPS:
        return False
    return OPS[op](facts[field], value)

def rule_matches(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    return all(evaluate_condition(facts, c) for c in rule["conditions"])

def run_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    fired = [r for r in rules if rule_matches(facts, r)]
    if not fired:
        return {"mode": "OFF", "reason": "No rule matched"}, []
    fired_sorted = sorted(fired, key=lambda r: r["priority"], reverse=True)
    return fired_sorted[0]["action"], fired_sorted

# ----------------------------
# 2) Streamlit UI
# ----------------------------
st.set_page_config(page_title="Smart AC Rule-Based System", layout="wide")
st.title("Smart Air Conditioner Rule-Based System")

with st.sidebar:
    st.header("Home Conditions")

    temperature = st.number_input("Temperature (°C)", value=22)
    humidity = st.number_input("Humidity (%)", value=46)
    occupancy = st.selectbox("Occupancy", ["OCCUPIED", "EMPTY"])
    time_of_day = st.selectbox("Time of Day", ["DAY", "NIGHT"])
    windows_open = st.checkbox("Windows Open", value=False)

    run = st.button("Evaluate", type="primary")

facts = {
    "temperature": temperature,
    "humidity": humidity,
    "occupancy": occupancy,
    "time_of_day": time_of_day,
    "windows_open": windows_open
}

st.subheader("Input Facts")
st.json(facts)

if run:
    action, fired = run_rules(facts, DEFAULT_RULES)

    st.subheader("Final AC Action")
    st.success(
        f"""
        **Mode:** {action['mode']}  
        **Fan Speed:** {action['fan_speed']}  
        **Setpoint:** {action['setpoint']}  
        **Reason:** {action['reason']}
        """
    )

    st.subheader("Matched Rules (by Priority)")
    for r in fired:
        st.write(f"• **{r['name']}** (priority {r['priority']})")

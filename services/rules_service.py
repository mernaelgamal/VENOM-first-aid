import json
import os
import tempfile
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "rules.json"


def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise ValueError("rules.json must contain a top-level rules list")
    return data


def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="rules_", suffix=".json", dir=DATA_FILE.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        os.replace(temp_name, DATA_FILE)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)


def get_rules():
    return load_data().get("rules", [])


def add_rule(new_rule):
    data = load_data()
    rules = data["rules"]
    rules.append(new_rule)
    save_data(data)
    return new_rule


def update_rule(rule_id, updated_data):
    data = load_data()
    for rule in data["rules"]:
        current_id = str(rule.get("rule_id") or rule.get("id") or "")
        if current_id == str(rule_id):
            rule.update(updated_data)
            save_data(data)
            return rule
    return None


def delete_rule(rule_id):
    data = load_data()
    rules = data["rules"]
    updated = [rule for rule in rules if str(rule.get("rule_id") or rule.get("id") or "") != str(rule_id)]
    if len(updated) == len(rules):
        return False
    data["rules"] = updated
    save_data(data)
    return True

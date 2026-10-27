from flask import Blueprint, jsonify, request

from auth import admin_required
from services.rules_service import get_rules, add_rule, update_rule, delete_rule

rules_bp = Blueprint("rules", __name__)
EDITABLE_FIELDS = {"condition", "action", "severity", "symptom_triggers", "referral"}


def _validate_rule(data, partial=False):
    if not isinstance(data, dict):
        return "A JSON object is required"
    if partial and not data:
        return "At least one field is required"
    if partial:
        if any(key not in EDITABLE_FIELDS for key in data):
            return "Invalid update fields"
    else:
        if any(key not in EDITABLE_FIELDS | {"rule_id", "id"} for key in data):
            return "Invalid rule fields"
        if not str(data.get("rule_id") or data.get("id") or "").strip():
            return "rule_id is required"
        for required in ("condition", "action"):
            if not isinstance(data.get(required), str) or not data[required].strip():
                return f"{required} is required"
    if "symptom_triggers" in data and not isinstance(data["symptom_triggers"], list):
        return "symptom_triggers must be a list"
    for field in ("condition", "action", "severity", "referral"):
        if field in data and not isinstance(data[field], str):
            return f"{field} must be a string"
    return None


@rules_bp.get("/api/rules")
def rules():
    try:
        data = get_rules()
        return jsonify({"status": "success", "count": len(data), "rules": data}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Unable to load rules"}), 500


@rules_bp.post("/api/rules")
@admin_required
def create_rule():
    data = request.get_json(silent=True)
    error = _validate_rule(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400
    rule_id = str(data.get("rule_id") or data.get("id")).strip()
    try:
        if any(str(rule.get("rule_id") or rule.get("id") or "") == rule_id for rule in get_rules()):
            return jsonify({"status": "error", "message": "A rule with this ID already exists"}), 409
        new_rule = dict(data)
        new_rule.pop("id", None)
        new_rule["rule_id"] = rule_id
        new_rule.setdefault("severity", "orange")
        new_rule.setdefault("symptom_triggers", [])
        new_rule.setdefault("referral", "")
        add_rule(new_rule)
        return jsonify({"status": "success", "rule": new_rule}), 201
    except Exception:
        return jsonify({"status": "error", "message": "Unable to save rule"}), 500


@rules_bp.put("/api/rules/<rule_id>")
@admin_required
def edit_rule(rule_id):
    data = request.get_json(silent=True)
    error = _validate_rule(data, partial=True)
    if error:
        return jsonify({"status": "error", "message": error}), 400
    try:
        updated = update_rule(rule_id, data)
        if updated is None:
            return jsonify({"status": "error", "message": "Rule not found"}), 404
        return jsonify({"status": "success", "rule": updated}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Unable to update rule"}), 500


@rules_bp.delete("/api/rules/<rule_id>")
@admin_required
def remove_rule(rule_id):
    try:
        deleted = delete_rule(rule_id)
        if not deleted:
            return jsonify({"status": "error", "message": "Rule not found"}), 404
        return jsonify({"status": "success", "message": "Rule deleted successfully"}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Unable to delete rule"}), 500

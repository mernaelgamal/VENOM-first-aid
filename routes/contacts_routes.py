from flask import Blueprint, jsonify, request

from auth import admin_required
from services.contact_service import (
    CONTACT_FIELDS, add_contact, delete_contact, get_contacts, update_contact,
)

contacts_bp = Blueprint("contacts", __name__)


def _validate_contact(data, partial=False):
    if not isinstance(data, dict):
        return "A JSON object is required"
    allowed = set(CONTACT_FIELDS)
    if any(key not in allowed for key in data):
        return "Invalid contact fields"
    if not partial:
        missing = [field for field in CONTACT_FIELDS if not str(data.get(field, "")).strip()]
        if missing:
            return "Required fields: " + ", ".join(missing)
    elif not data:
        return "At least one field is required"
    return None


@contacts_bp.get("/api/contacts")
def contacts():
    try:
        data = get_contacts()
        return jsonify({"status": "success", "count": len(data), "contacts": data}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Unable to load contacts"}), 500


@contacts_bp.post("/api/contacts")
@admin_required
def create_contact():
    data = request.get_json(silent=True)
    error = _validate_contact(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400
    try:
        contact = add_contact(data)
        return jsonify({"status": "success", "contact": contact}), 201
    except Exception:
        return jsonify({"status": "error", "message": "Unable to save contact"}), 500


@contacts_bp.put("/api/contacts/<int:record_id>")
@admin_required
def edit_contact(record_id):
    data = request.get_json(silent=True)
    error = _validate_contact(data, partial=True)
    if error:
        return jsonify({"status": "error", "message": error}), 400
    try:
        contact = update_contact(record_id, data)
        if contact is None:
            return jsonify({"status": "error", "message": "Contact not found"}), 404
        return jsonify({"status": "success", "contact": contact}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Unable to update contact"}), 500


@contacts_bp.delete("/api/contacts/<int:record_id>")
@admin_required
def remove_contact(record_id):
    try:
        if not delete_contact(record_id):
            return jsonify({"status": "error", "message": "Contact not found"}), 404
        return jsonify({"status": "success", "message": "Contact deleted"}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Unable to delete contact"}), 500

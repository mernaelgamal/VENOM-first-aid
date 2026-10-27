from flask import Blueprint, jsonify, request, redirect, url_for

from auth import admin_required
from services.clinics_service import EDITABLE_FIELDS, add_clinic as save_clinic, delete_clinic, get_clinics, update_clinic

clinics_bp = Blueprint("clinics", __name__)


def _validate_clinic(data, partial=False):
    if not isinstance(data, dict):
        return "A JSON object is required"
    if any(key not in EDITABLE_FIELDS for key in data):
        return "Invalid clinic fields"
    if not partial and not str(data.get("name", "")).strip():
        return "Clinic name is required"
    if partial and not data:
        return "At least one field is required"
    for field, low, high in (("lat", -90, 90), ("lon", -180, 180)):
        if field in data and str(data[field]).strip():
            try:
                number = float(data[field])
            except (TypeError, ValueError):
                return f"{field} must be a number"
            if not low <= number <= high:
                return f"{field} is out of range"
    return None


@clinics_bp.get("/api/clinics")
def clinic_list():
    try:
        rows = get_clinics()
        return jsonify({"count": len(rows), "clinics": rows}), 200
    except Exception:
        return jsonify({"error": "Could not read clinics data"}), 500


@clinics_bp.post("/admin/clinics/add")
@admin_required
def add_clinic_from_form():
    data = {field: request.form.get(field, "").strip() for field in EDITABLE_FIELDS}
    error = _validate_clinic(data)
    if error:
        return error, 400
    try:
        save_clinic(data)
        return redirect(url_for("admin_panel") + "#clinics")
    except Exception:
        return "حدث خطأ أثناء حفظ بيانات العيادة. راجعي ملف CSV وصلاحيات الكتابة.", 500


@clinics_bp.post("/api/clinics")
@admin_required
def create_clinic():
    data = request.get_json(silent=True)
    error = _validate_clinic(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400
    try:
        clinic = save_clinic(data)
        return jsonify({"status": "success", "clinic": clinic}), 201
    except Exception:
        return jsonify({"status": "error", "message": "Unable to save clinic"}), 500


@clinics_bp.put("/api/clinics/<clinic_id>")
@admin_required
def edit_clinic(clinic_id):
    data = request.get_json(silent=True)
    error = _validate_clinic(data, partial=True)
    if error:
        return jsonify({"status": "error", "message": error}), 400
    try:
        clinic = update_clinic(clinic_id, data)
        if clinic is None:
            return jsonify({"status": "error", "message": "Clinic not found"}), 404
        return jsonify({"status": "success", "clinic": clinic}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Unable to update clinic"}), 500


@clinics_bp.delete("/api/clinics/<clinic_id>")
@admin_required
def remove_clinic(clinic_id):
    try:
        if not delete_clinic(clinic_id):
            return jsonify({"status": "error", "message": "Clinic not found"}), 404
        return jsonify({"status": "success", "message": "Clinic deleted"}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Unable to delete clinic"}), 500

from flask import Blueprint, jsonify, request
from auth import admin_required
from services.analytics_service import log_search, get_search_stats

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/api/analytics", methods=["GET"])
@admin_required
def analytics():
    try:
        stats = get_search_stats()

        return jsonify({
            "status": "success",
            "analytics": stats
        }), 200

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Unable to load analytics"
        }), 500


@analytics_bp.route("/api/analytics/search", methods=["POST"])
def record_search():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A JSON object is required"
        }), 400

    query = data.get("query")

    if not isinstance(query, str) or not query.strip():
        return jsonify({
            "status": "error",
            "message": "A valid search query is required"
        }), 400

    try:
        log_search(query.strip())

        return jsonify({
            "status": "success",
            "message": "Search recorded successfully"
        }), 201

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Unable to record search"
        }), 500


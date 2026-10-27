from flask import Blueprint, request, jsonify
from services.analytics_service import log_search
from services.search_service import search_guides

search_bp = Blueprint("search", __name__)


@search_bp.route("/api/search", methods=["POST"])
def search():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    query = data.get("query", "")

    if not isinstance(query, str) or not query.strip():
        return jsonify({
            "error": "Please provide a valid search query"
        }), 400

    query = query.strip()

    try:
        results = search_guides(query)

        log_search(query)

        return jsonify({
            "query": query,
            "results": results,
            "count": len(results),
            "status": "success"
        }), 200

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Unable to complete search"
        }), 500


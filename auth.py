"""Authentication and CSRF checks for administrator-only routes."""
from functools import wraps
import hmac
from flask import jsonify, redirect, request, session, url_for


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            if request.path.startswith("/api/"):
                return jsonify({"status": "error", "message": "Administrator login required"}), 401
            return redirect(url_for("admin_login"))

        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            expected = session.get("csrf_token", "")
            supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
            if not expected or not supplied or not hmac.compare_digest(str(expected), str(supplied)):
                if request.path.startswith("/api/"):
                    return jsonify({"status": "error", "message": "Invalid or missing CSRF token"}), 400
                return "انتهت صلاحية النموذج. حدّثي الصفحة وحاولي مرة أخرى.", 400

        return view(*args, **kwargs)
    return wrapped

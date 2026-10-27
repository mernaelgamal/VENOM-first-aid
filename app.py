import os
import secrets
import time
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from auth import admin_required
from routes.search_routes import search_bp
from routes.contacts_routes import contacts_bp
from routes.rules_routes import rules_bp
from routes.analytics_routes import analytics_bp
from routes.clinics_routes import clinics_bp
from routes.dashboard_routes import dashboard_bp

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV == "production" or bool(os.getenv("RENDER")) or bool(os.getenv("VERCEL"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

if IS_PRODUCTION and not ADMIN_PASSWORD:
    raise RuntimeError("Set ADMIN_PASSWORD in your deployment environment before starting the app.")
if IS_PRODUCTION and not FLASK_SECRET_KEY:
    raise RuntimeError("Set FLASK_SECRET_KEY in your deployment environment before starting the app.")

# Keep the existing local workflow convenient, but never use the development defaults publicly.
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = "VENOM"
    print("WARNING: using the temporary local admin password. Set ADMIN_PASSWORD in .env before deployment.")
if not FLASK_SECRET_KEY:
    FLASK_SECRET_KEY = secrets.token_hex(32)
    print("WARNING: using a temporary local session key. Set FLASK_SECRET_KEY in .env for stable sessions.")

# Static files live in public/ and are served from the site root (/css/..., /js/...).
# This works locally with Flask and on Vercel (which serves public/ itself).
app = Flask(__name__, static_folder="public", static_url_path="")
app.secret_key = FLASK_SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
)


DATA_DIR = BASE_DIR / "data"
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
# Public endpoints that may fail silently when storage is read-only (search logging is skipped).
PUBLIC_POSTS = {"/login", "/api/search", "/api/analytics/search"}


@app.before_request
def block_writes_on_read_only_storage():
    """On read-only hosts (e.g. Vercel) tell the admin clearly that edits cannot be saved."""
    if request.method not in WRITE_METHODS or request.path in PUBLIC_POSTS:
        return None
    if not session.get("logged_in"):
        return None  # let the normal login check answer first
    if os.access(DATA_DIR, os.W_OK):
        return None
    message = ("التخزين للقراءة فقط في هذه البيئة، لذلك لا يمكن حفظ التعديلات. "
               "Storage is read-only here, so changes cannot be saved.")
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": message}), 503
    return message, 503


@app.get("/admin")
@admin_required
def admin_panel():
    session.setdefault("csrf_token", secrets.token_urlsafe(32))
    return render_template("admin.html", csrf_token=session["csrf_token"])


@app.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        # Compare as bytes so non-ASCII (e.g. Arabic) passwords never raise an error.
        if secrets.compare_digest(password.encode("utf-8"), ADMIN_PASSWORD.encode("utf-8")):
            session.clear()
            session["logged_in"] = True
            return redirect(url_for("admin_panel"))
        time.sleep(1)  # slows down password guessing
        return '''
            <!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8">
            <title>تسجيل الدخول</title>
            <body style="text-align:center;padding-top:100px;font-family:sans-serif;background:#101522;color:white;min-height:100vh">
            <h3 style="color:#e74c3c">كلمة المرور غير صحيحة!</h3>
            <a href="/login" style="color:#8dc8ff">حاولي مرة أخرى</a></body></html>
        ''', 401

    return '''
        <!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>تسجيل دخول لوحة التحكم</title>
        <body style="text-align:center;padding:100px 20px 20px;font-family:Segoe UI,Tahoma,Arial,sans-serif;background:#101522;color:white;min-height:100vh;box-sizing:border-box">
        <h2>تسجيل دخول لوحة التحكم</h2>
        <form method="POST" style="margin-top:20px">
            <label for="password">كلمة المرور</label><br><br>
            <input id="password" type="password" name="password" autocomplete="current-password" placeholder="أدخلي كلمة المرور" style="padding:10px;width:min(280px,80%);border-radius:6px;border:none" required>
            <button type="submit" style="padding:10px 20px;background:#e74c3c;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold">دخول</button>
        </form></body></html>
    '''


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok"}), 200


app.register_blueprint(search_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(rules_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(clinics_bp)
app.register_blueprint(dashboard_bp)


@app.get("/")
def home():
    return redirect(url_for("admin_panel"))


if __name__ == "__main__":
    app.run(debug=(APP_ENV != "production"), use_reloader=(APP_ENV != "production"))

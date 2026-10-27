import csv
import io
import os
import tempfile
from collections import Counter
from pathlib import Path

from flask import Blueprint, jsonify, request

from auth import admin_required

dashboard_bp = Blueprint("dashboard", __name__)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA = DATA_DIR / "contacts_and_clinics.csv"
CLINICS = DATA_DIR / "clinics.csv"
FIELDS = ["contact_id", "service_name_ar", "governorate", "city_area", "phone_number",
          "hotline", "category", "address", "available_hours", "services_provided"]
EDITABLE = FIELDS[1:]


def _read():
    with DATA.open("r", encoding="utf-8-sig", newline="") as f:
        return [{k: (r.get(k) or "").strip() for k in FIELDS} for r in csv.DictReader(f)]


def _write(rows):
    fd, tmp = tempfile.mkstemp(prefix="entities_", suffix=".csv", dir=DATA.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, DATA)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _next_id(rows):
    ids = [int(r["contact_id"]) for r in rows if r["contact_id"].isdigit()]
    return str(max(ids, default=0) + 1)


def _clean(data):
    return {k: str(data.get(k, "")).strip()[:500] for k in EDITABLE}


@dashboard_bp.get("/api/dashboard/summary")
@admin_required
def summary():
    rows = _read()
    gov = Counter(r["governorate"] for r in rows if r["governorate"])
    cat = Counter(r["category"] for r in rows if r["category"])
    top = cat.most_common(5)
    other = sum(cat.values()) - sum(n for _, n in top)
    if other:
        top.append(("__other__", other))
    points = []
    if CLINICS.exists():
        with CLINICS.open("r", encoding="utf-8-sig", newline="") as f:
            seen = set()
            for r in csv.DictReader(f):
                try:
                    p = (round(float(r["lat"]), 3), round(float(r["lon"]), 3))
                except (KeyError, TypeError, ValueError):
                    continue
                if p not in seen:
                    seen.add(p)
                    points.append({"lat": p[0], "lon": p[1], "name": (r.get("name") or "")[:60]})
    return jsonify({
        "total": len(rows), "hospitals": sum(n for k, n in cat.items() if "مستشفى" in k),
        "governorates": len(gov), "categories": len(cat),
        "by_governorate": gov.most_common(7), "by_category": top,
        "gov_all": gov.most_common(), "cat_all": cat.most_common(), "points": points,
    })


@dashboard_bp.get("/api/entities")
@admin_required
def list_entities():
    rows = _read()[::-1]
    q = request.args.get("q", "").strip().lower()
    if q:
        rows = [r for r in rows if q in " ".join(r.values()).lower()]
    per = min(max(request.args.get("per_page", 5, type=int), 1), 50)
    page = max(request.args.get("page", 1, type=int), 1)
    return jsonify({"total": len(rows), "page": page, "per_page": per,
                    "rows": rows[(page - 1) * per: page * per]})


@dashboard_bp.post("/api/entities")
@admin_required
def create_entity():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("service_name_ar", "")).strip():
        return jsonify({"status": "error", "message": "Name is required"}), 400
    rows = _read()
    row = _clean(data)
    row["contact_id"] = _next_id(rows)
    rows.append(row)
    _write(rows)
    return jsonify({"status": "success", "entity": row}), 201


@dashboard_bp.put("/api/entities/<entity_id>")
@admin_required
def update_entity(entity_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("service_name_ar", "x")).strip():
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    rows = _read()
    for r in rows:
        if r["contact_id"] == entity_id:
            r.update({k: v for k, v in _clean(data).items() if k in data})
            _write(rows)
            return jsonify({"status": "success", "entity": r})
    return jsonify({"status": "error", "message": "Not found"}), 404


@dashboard_bp.delete("/api/entities/<entity_id>")
@admin_required
def delete_entity(entity_id):
    rows = _read()
    kept = [r for r in rows if r["contact_id"] != entity_id]
    if len(kept) == len(rows):
        return jsonify({"status": "error", "message": "Not found"}), 404
    _write(kept)
    return jsonify({"status": "success"})


@dashboard_bp.post("/api/import")
@admin_required
def import_csv():
    f = request.files.get("file")
    if not f:
        return jsonify({"status": "error", "message": "No file"}), 400
    raw = f.read(1_000_001)
    if len(raw) > 1_000_000:
        return jsonify({"status": "error", "message": "File too large (max 1MB)"}), 400
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        if "service_name_ar" not in (reader.fieldnames or []):
            return jsonify({"status": "error", "message": "Missing column: service_name_ar"}), 400
        new = [r for r in reader if (r.get("service_name_ar") or "").strip()][:2000]
    except (UnicodeDecodeError, csv.Error):
        return jsonify({"status": "error", "message": "Could not read CSV (use UTF-8)"}), 400
    rows = _read()
    start = int(_next_id(rows))
    for i, r in enumerate(new):
        row = _clean(r)
        row["contact_id"] = str(start + i)
        rows.append(row)
    _write(rows)
    return jsonify({"status": "success", "imported": len(new)})

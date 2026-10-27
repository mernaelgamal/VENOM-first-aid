import csv
import os
import tempfile
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "clinics.csv"
CLINIC_FIELDS = ["id", "name", "building", "floor", "phone", "lat", "lon", "hours"]
EDITABLE_FIELDS = ["name", "building", "floor", "phone", "lat", "lon", "hours"]


def get_clinics():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = []
        for raw in reader:
            rows.append({field: (raw.get(field) or "").strip() for field in CLINIC_FIELDS})
        return rows


def _write_rows(rows):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="clinics_", suffix=".csv", dir=DATA_FILE.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=CLINIC_FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_name, DATA_FILE)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)


def _next_id(rows):
    highest = 0
    for row in rows:
        identifier = str(row.get("id", ""))
        if identifier.startswith("clinic_"):
            suffix = identifier.removeprefix("clinic_")
            if suffix.isdigit():
                highest = max(highest, int(suffix))
    return f"clinic_{highest + 1:03d}"


def add_clinic(data):
    rows = get_clinics()
    row = {field: str(data.get(field, "")).strip() for field in EDITABLE_FIELDS}
    row["id"] = _next_id(rows)
    rows.append(row)
    _write_rows(rows)
    return row


def update_clinic(clinic_id, updates):
    rows = get_clinics()
    for row in rows:
        if row["id"] == clinic_id:
            for field in EDITABLE_FIELDS:
                if field in updates:
                    row[field] = str(updates[field]).strip()
            _write_rows(rows)
            return row
    return None


def delete_clinic(clinic_id):
    rows = get_clinics()
    updated = [row for row in rows if row["id"] != clinic_id]
    if len(updated) == len(rows):
        return False
    _write_rows(updated)
    return True

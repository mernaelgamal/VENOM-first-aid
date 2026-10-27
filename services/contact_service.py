import csv
import os
import tempfile
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "contacts.csv"
CONTACT_FIELDS = ["name", "phone", "type", "available_hours", "campus_area"]


def _read_rows():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = []
        for row in reader:
            rows.append({field: (row.get(field) or "").strip() for field in CONTACT_FIELDS})
        return rows


def _write_rows(rows):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="contacts_", suffix=".csv", dir=DATA_FILE.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=CONTACT_FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_name, DATA_FILE)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)


def get_contacts():
    return [dict(row, _record_id=str(index)) for index, row in enumerate(_read_rows())]


def add_contact(contact):
    rows = _read_rows()
    clean = {field: str(contact.get(field, "")).strip() for field in CONTACT_FIELDS}
    rows.append(clean)
    _write_rows(rows)
    return dict(clean, _record_id=str(len(rows) - 1))


def update_contact(record_id, updates):
    rows = _read_rows()
    if record_id < 0 or record_id >= len(rows):
        return None
    for field in CONTACT_FIELDS:
        if field in updates:
            rows[record_id][field] = str(updates[field]).strip()
    _write_rows(rows)
    return dict(rows[record_id], _record_id=str(record_id))


def delete_contact(record_id):
    rows = _read_rows()
    if record_id < 0 or record_id >= len(rows):
        return False
    rows.pop(record_id)
    _write_rows(rows)
    return True

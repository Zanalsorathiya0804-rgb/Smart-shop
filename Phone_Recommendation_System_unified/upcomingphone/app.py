
from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import json, datetime

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
PHONES_FILE = DATA_DIR / "upcoming_phones.json"
NOTIFS_FILE = DATA_DIR / "notifications.json"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

def load_phones():
    try:
        with open(PHONES_FILE, "r", encoding="utf-8") as f:
            phones = json.load(f)
            # ensure release_date parsed to ISO date string
            for p in phones:
                p["release_date"] = p.get("release_date")
            return phones
    except FileNotFoundError:
        return []

def read_notifications():
    try:
        with open(NOTIFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_notifications(lst):
    with open(NOTIFS_FILE, "w", encoding="utf-8") as f:
        json.dump(lst, f, indent=2, ensure_ascii=False)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/upcoming", methods=["GET"])
def api_upcoming():
    """
    Query params:
      - q: text search in model/brand/description
      - brand: exact brand match (case-insensitive)
      - days: integer (show upcoming within next N days). default: 365
      - all: if "1", show all (past and future)
      - sort: "soon" or "latest" (soon = release_date ascending)
    """
    phones = load_phones()
    q = (request.args.get("q") or "").strip().lower()
    brand = (request.args.get("brand") or "").strip().lower()
    days = request.args.get("days", type=int)
    show_all = request.args.get("all") == "1"
    sort = (request.args.get("sort") or "soon").strip().lower()

    today = datetime.date.today()

    results = []
    for p in phones:
        rd_str = p.get("release_date")
        try:
            rd = datetime.datetime.strptime(rd_str, "%Y-%m-%d").date() if rd_str else None
        except Exception:
            rd = None
        # filters
        if q:
            txt = " ".join([str(p.get(k,"")).lower() for k in ("brand","model","description","notes")])
            if q not in txt:
                continue
        if brand and p.get("brand","").strip().lower() != brand:
            continue
        if not show_all and rd:
            if days is None:
                days = 365
            if rd < today or (rd - today).days > days:
                continue
        # compute days_until if rd present
        days_until = None
        if rd:
            days_until = (rd - today).days
        item = dict(p)
        item["_days_until"] = days_until
        results.append(item)

    # sort
    if sort == "soon":
        results.sort(key=lambda x: (x["_days_until"] if x["_days_until"] is not None else 99999))
    else:
        results.sort(key=lambda x: (x["_days_until"] if x["_days_until"] is not None else 99999), reverse=True)

    return jsonify({"total": len(results), "results": results})

@app.route("/api/phone/<pid>", methods=["GET"])
def api_phone(pid):
    phones = load_phones()
    for p in phones:
        if p.get("id") == pid:
            return jsonify({"status":"ok","phone":p})
    return jsonify({"status":"error","message":"not found"}), 404

@app.route("/api/notify", methods=["POST"])
def api_notify():
    """
    POST JSON or form: { "phone_id": "<id>", "name": "...", "contact": "...", "notes": "..." }
    Stores notification request locally in data/notifications.json
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    phone_id = data.get("phone_id")
    name = data.get("name","").strip()
    contact = data.get("contact","").strip()
    notes = data.get("notes","").strip()

    if not phone_id:
        return jsonify({"status":"error","message":"phone_id required"}), 400

    notifs = read_notifications()
    entry = {
        "phone_id": phone_id,
        "name": name,
        "contact": contact,
        "notes": notes,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    notifs.append(entry)
    write_notifications(notifs)
    return jsonify({"status":"ok","entry":entry})

@app.route("/api/notifications", methods=["GET"])
def api_notifications():
    # admin helper to list saved notifications
    notifs = read_notifications()
    return jsonify({"total": len(notifs), "results": notifs})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=True)

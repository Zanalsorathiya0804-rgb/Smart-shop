
from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import json, time
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
LISTINGS_FILE = DATA_DIR / "listings.json"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

def read_listings():
    try:
        with open(LISTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_listings(lst):
    with open(LISTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(lst, f, indent=2, ensure_ascii=False)

@app.route("/")
def home():
    return app.send_static_file("used.html")

@app.route("/used.html")
def used_page():
    return app.send_static_file("used.html")

@app.route("/api/listings", methods=["GET"])
def api_listings():
    """
    Query params:
      - q: search by brand or model (contains)
      - city, state
      - type: sell|buy
      - status: available|sold (default available)
    """
    q = (request.args.get("q") or "").strip().lower()
    city = (request.args.get("city") or "").strip().lower()
    state = (request.args.get("state") or "").strip().lower()
    ltype = (request.args.get("type") or "").strip().lower()
    status = (request.args.get("status") or "available").strip().lower()

    all_listings = read_listings()
    def matches(item):
        if status and item.get("status","") != status:
            return False
        if ltype and item.get("type","") != ltype:
            return False
        if city and item.get("city","").strip().lower() != city:
            return False
        if state and item.get("state","").strip().lower() != state:
            return False
        if q:
            txt = " ".join([str(item.get(k,"")).lower() for k in ("brand","model","description")])
            if q not in txt:
                return False
        return True

    results = [i for i in all_listings if matches(i)]
    # newest first
    results.sort(key=lambda x: x.get("posted_at",""), reverse=True)
    return jsonify({"total": len(results), "results": results})

@app.route("/api/listings", methods=["POST"])
def api_post_listing():
    """
    Accepts JSON or form data for a new listing.
    Required for SELL: type='sell', seller_name, contact_phone, brand, model, price, condition, city, state
    For BUY: type='buy' - most fields optional
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    ltype = (data.get("type") or "sell").strip().lower()

    # minimal validation
    if ltype not in ("sell","buy"):
        return jsonify({"status":"error","message":"type must be 'sell' or 'buy'"}), 400

    # enforce required for sell
    if ltype == "sell":
        required = ["seller_name","contact_phone","brand","model","price","condition","city","state"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"status":"error","message":"missing fields for sell: "+", ".join(missing)}), 400

    # build listing object
    listings = read_listings()
    lid = f"L{int(time.time()*1000)}"
    listing = {
        "id": lid,
        "type": ltype,
        "brand": data.get("brand","").strip(),
        "model": data.get("model","").strip(),
        "condition": data.get("condition","").strip(),
        "price": float(data.get("price") or 0),
        "description": data.get("description","").strip(),
        "city": data.get("city","").strip(),
        "state": data.get("state","").strip(),
        "seller_name": data.get("seller_name","").strip(),
        "contact_phone": data.get("contact_phone","").strip(),
        "images": data.get("images") or [],
        "status": "available",
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    listings.append(listing)
    write_listings(listings)
    return jsonify({"status":"ok","listing":listing})

@app.route("/api/mark_sold", methods=["POST"])
def api_mark_sold():
    """
    JSON body: { "id": "<listing id>" }
    Marks listing as sold (status='sold')
    """
    data = request.get_json(silent=True) or {}
    lid = data.get("id")
    if not lid:
        return jsonify({"status":"error","message":"missing id"}), 400
    listings = read_listings()
    found = False
    for l in listings:
        if l.get("id") == lid:
            l["status"] = "sold"
            found = True
            break
    if not found:
        return jsonify({"status":"error","message":"id not found"}), 404
    write_listings(listings)
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)


from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

def load_json(filename):
    with open(STATIC_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize(s):
    return (s or "").strip().lower()

@app.route("/")
def home():
    # Serve the Phone Finder page
    return app.send_static_file("index.html")

@app.route("/shops.html")
def shops_page():
    # Serve the Shop Locator page
    return app.send_static_file("shops.html")

@app.route("/api/phones", methods=["GET"])
def api_phones():
    """
    Query params supported:
      - q: search text (brand or model contains)
      - brand: exact brand match (case-insensitive)
      - min_price, max_price: integers
      - ram_min: integer (GB)
      - storage_min: integer (GB)
      - sort: price_asc | price_desc | rating_desc
      - model_id: exact id to fetch a single phone
    """
    phones = load_json("phones.json")

    q = normalize(request.args.get("q"))
    brand = normalize(request.args.get("brand"))
    model_id = request.args.get("model_id")
    min_price = request.args.get("min_price", type=int)
    max_price = request.args.get("max_price", type=int)
    ram_min = request.args.get("ram_min", type=int)
    storage_min = request.args.get("storage_min", type=int)
    sort = request.args.get("sort")

    def matches(p):
        if model_id and p.get("id") != model_id:
            return False
        if brand and normalize(p.get("brand")) != brand:
            return False
        if q and (q not in normalize(p.get("brand")) and q not in normalize(p.get("model"))):
            return False
        if min_price is not None and p.get("price", 0) < min_price:
            return False
        if max_price is not None and p.get("price", 0) > max_price:
            return False
        if ram_min is not None and p.get("ram_gb", 0) < ram_min:
            return False
        if storage_min is not None and p.get("storage_gb", 0) < storage_min:
            return False
        return True

    results = [p for p in phones if matches(p)]

    if sort == "price_asc":
        results.sort(key=lambda x: x.get("price", 0))
    elif sort == "price_desc":
        results.sort(key=lambda x: x.get("price", 0), reverse=True)
    elif sort == "rating_desc":
        results.sort(key=lambda x: x.get("rating", 0), reverse=True)

    return jsonify({"total": len(results), "results": results})

@app.route("/api/shops", methods=["GET"])
def api_shops():
    """
    Query params:
      - city: string
      - state: string
      - model_id (optional): filter shops that have this phone in inventory
      - brand (optional): fallback filter by brand support if model not provided
    """
    shops = load_json("shops.json")
    city = normalize(request.args.get("city"))
    state = normalize(request.args.get("state"))
    model_id = request.args.get("model_id")
    brand = normalize(request.args.get("brand"))

    def matches(shop):
        if city and normalize(shop.get("city")) != city:
            return False
        if state and normalize(shop.get("state")) != state:
            return False
        if model_id:
            inv = set(shop.get("inventory", []))
            return model_id in inv
        if brand:
            return brand in [normalize(b) for b in shop.get("phone_brands", [])]
        return True

    results = [s for s in shops if matches(s)]
    return jsonify({"total": len(results), "results": results})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

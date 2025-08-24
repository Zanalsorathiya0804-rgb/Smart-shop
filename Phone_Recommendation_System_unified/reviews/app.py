
from flask import Flask, request, jsonify
from pathlib import Path
import json, datetime, time

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REV_FILE = DATA_DIR / "reviews.json"

app = Flask(__name__, static_folder=str(BASE_DIR / "static"), static_url_path="")

def read_reviews():
    try:
        with open(REV_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_reviews(lst):
    with open(REV_FILE, "w", encoding="utf-8") as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/reviews", methods=["GET"])
def api_get_reviews():
    """
    Query params:
      - q: text search in title/body
      - model: filter by phone model
      - min_rating: integer 1-5
      - city: filter by city
      - sort: newest | highest (default newest)
    """
    q = (request.args.get("q") or "").strip().lower()
    model = (request.args.get("model") or "").strip().lower()
    city = (request.args.get("city") or "").strip().lower()
    min_rating = request.args.get("min_rating", type=int)
    sort = (request.args.get("sort") or "newest").strip().lower()

    reviews = read_reviews()
    def matches(r):
        if model and r.get("model","").strip().lower() != model:
            return False
        if city and r.get("city","").strip().lower() != city:
            return False
        if min_rating and int(r.get("rating",0)) < min_rating:
            return False
        if q:
            txt = " ".join([str(r.get(k,"")).lower() for k in ("title","body","reviewer_name","model")])
            if q not in txt:
                return False
        return True

    filtered = [r for r in reviews if matches(r)]
    if sort == "highest":
        filtered.sort(key=lambda x: int(x.get("rating",0)), reverse=True)
    else:
        filtered.sort(key=lambda x: x.get("created_at"), reverse=True)

    # compute average rating for convenience
    avg = None
    if filtered:
        avg = sum(int(r.get("rating",0)) for r in filtered) / len(filtered)
    return jsonify({"total": len(filtered), "avg_rating": round(avg,2) if avg is not None else None, "results": filtered})

@app.route("/api/reviews", methods=["POST"])
def api_post_review():
    """
    Accepts JSON or form data:
      - reviewer_name (optional)
      - rating (required, 1-5)
      - title (optional)
      - body (required)
      - model (optional)
      - city (optional)
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    try:
        rating = int(data.get("rating", 0))
    except Exception:
        rating = 0
    body = (data.get("body") or "").strip()
    if rating < 1 or rating > 5:
        return jsonify({"status":"error","message":"rating must be 1..5"}), 400
    if not body:
        return jsonify({"status":"error","message":"body is required"}), 400

    reviews = read_reviews()
    rid = f"R{int(time.time()*1000)}"
    entry = {
        "id": rid,
        "reviewer_name": (data.get("reviewer_name") or "").strip(),
        "rating": rating,
        "title": (data.get("title") or "").strip(),
        "body": body,
        "model": (data.get("model") or "").strip(),
        "city": (data.get("city") or "").strip(),
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "visible": True
    }
    reviews.append(entry)
    write_reviews(reviews)
    return jsonify({"status":"ok","review":entry})

@app.route("/api/reviews/<rid>/hide", methods=["POST"])
def api_hide_review(rid):
    """
    Simple moderation endpoint to hide a review (no auth in starter).
    POSTing marks visible=False.
    """
    reviews = read_reviews()
    found = False
    for r in reviews:
        if r.get("id") == rid:
            r["visible"] = False
            found = True
            break
    if not found:
        return jsonify({"status":"error","message":"not found"}), 404
    write_reviews(reviews)
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005, debug=True)

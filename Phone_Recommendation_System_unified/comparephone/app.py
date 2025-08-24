
from flask import Flask, jsonify, request
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

PHONES_FILE = STATIC_DIR / "phones.json"

def load_phones():
    with open(PHONES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/phones", methods=["GET"])
def api_phones():
    phones = load_phones()
    return jsonify({"total": len(phones), "results": phones})

@app.route("/api/phone/<pid>", methods=["GET"])
def api_phone(pid):
    phones = load_phones()
    for p in phones:
        if p["id"] == pid:
            return jsonify({"status":"ok","phone":p})
    return jsonify({"status":"error","message":"not found"}), 404

@app.route("/api/compare", methods=["POST"])
def api_compare():
    data = request.get_json(silent=True) or {}
    id1 = data.get("id1")
    id2 = data.get("id2")
    if not id1 or not id2:
        return jsonify({"status":"error","message":"provide id1 and id2"}), 400
    phones = load_phones()
    p1 = next((p for p in phones if p["id"]==id1), None)
    p2 = next((p for p in phones if p["id"]==id2), None)
    if not p1 or not p2:
        return jsonify({"status":"error","message":"one or both ids not found"}), 404

    # Specs to consider and weights
    specs = {
        "rating": {"higher_is_better": True, "weight": 0.30, "label":"Rating (out of 5)"},
        "price": {"higher_is_better": False, "weight": 0.25, "label":"Price (INR)"},
        "ram_gb": {"higher_is_better": True, "weight": 0.15, "label":"RAM (GB)"},
        "storage_gb": {"higher_is_better": True, "weight": 0.10, "label":"Storage (GB)"},
        "battery_mah": {"higher_is_better": True, "weight": 0.12, "label":"Battery (mAh)"},
        "camera_mp": {"higher_is_better": True, "weight": 0.08, "label":"Camera (MP)"}
    }

    # gather values
    values = {}
    for key in specs:
        v1 = float(p1.get(key) or 0)
        v2 = float(p2.get(key) or 0)
        values[key] = (v1, v2)

    # normalize and score
    total1 = 0.0
    total2 = 0.0
    per_spec = []
    for key, info in specs.items():
        v1, v2 = values[key]
        higher_better = info["higher_is_better"]
        weight = info["weight"]
        # normalization between the two values
        mx = max(v1, v2)
        mn = min(v1, v2)
        if mx == mn:
            s1 = s2 = 0.5
        else:
            if higher_better:
                s1 = (v1 - mn) / (mx - mn)
                s2 = (v2 - mn) / (mx - mn)
            else:
                # lower is better (price)
                s1 = (mx - v1) / (mx - mn)
                s2 = (mx - v2) / (mx - mn)
        total1 += weight * s1
        total2 += weight * s2
        # decide winner for this spec
        if abs(s1 - s2) < 1e-9:
            winner = "tie"
        elif s1 > s2:
            winner = "left"
        else:
            winner = "right"
        per_spec.append({
            "spec": key,
            "label": info.get("label", key),
            "left_value": v1,
            "right_value": v2,
            "left_score": round(s1, 3),
            "right_score": round(s2, 3),
            "winner": winner
        })

    score1 = round(total1 * 100, 2)
    score2 = round(total2 * 100, 2)

    # generate textual explanation
    reasons = []
    for ps in per_spec:
        if ps["winner"] == "left":
            reasons.append(f"{p1['brand']} {p1['model']} has better {ps['label']} ({ps['left_value']} vs {ps['right_value']}).")
        elif ps["winner"] == "right":
            reasons.append(f"{p2['brand']} {p2['model']} has better {ps['label']} ({ps['right_value']} vs {ps['left_value']}).")

    # pick recommendation
    if score1 == score2:
        recommended = None
        summary = "Both phones score equally based on the selected specs and weights."
    elif score1 > score2:
        recommended = {"id": p1["id"], "brand": p1["brand"], "model": p1["model"], "score": score1}
        summary = f"Recommendation: {p1['brand']} {p1['model']} (score {score1} vs {score2}) because: " + " ".join(reasons[:3])
    else:
        recommended = {"id": p2["id"], "brand": p2["brand"], "model": p2["model"], "score": score2}
        summary = f"Recommendation: {p2['brand']} {p2['model']} (score {score2} vs {score1}) because: " + " ".join(reasons[:3])

    return jsonify({
        "status":"ok",
        "left": p1,
        "right": p2,
        "per_spec": per_spec,
        "score_left": score1,
        "score_right": score2,
        "recommended": recommended,
        "summary": summary,
        "explanations": reasons
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=True)

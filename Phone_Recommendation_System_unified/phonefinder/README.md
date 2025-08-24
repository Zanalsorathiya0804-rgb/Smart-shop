
# Smart Shop — Phone Finder (HTML/CSS/JS + Python/Flask)

This is a minimal but complete starter you can run locally.

## 1) Prerequisites
- Python 3.8+ installed
- pip installed

## 2) Install dependencies
```bash
pip install flask
```

## 3) Run the server
From this folder:
```bash
python app.py
```
Then open http://127.0.0.1:5000 in your browser.

## 4) What’s included
- `app.py` — Flask backend with two APIs:
  - `GET /api/phones` — filters phone catalog by query, brand, price, RAM, storage, sort.
  - `GET /api/shops` — returns shops filtered by city/state and phone model or brand.
- `static/index.html` — Phone Finder UI with filters and **Buy Now** button.
- `static/shops.html` — Shop Locator page (enter City/State to see shops).
- `static/app.js` — Frontend logic (fetch APIs, render cards).
- `static/styles.css` — Minimal modern styling.
- `static/phones.json` — Sample phone data (India-focused).
- `static/shops.json` — Sample shop data for major Indian cities.

## 5) How the flow works
1. Open `/` to see the Phone Finder.
2. Use filters, hit **Search** to load matching phones.
3. Click **Buy Now** on any phone → navigates to `/shops.html?model_id=...&brand=...`.
4. Enter your **City** and **State** (e.g., Ahmedabad, Gujarat) → **Find Shops**.
5. You’ll get shops carrying that exact model (or at least the brand).

## 6) Customize / Extend
- Add more phones to `static/phones.json` and shops to `static/shops.json`.
- Replace text inputs for city/state with dropdowns to avoid spelling issues.
- Add geolocation + map (Leaflet + OpenStreetMap) and distance sorting.
- Switch to a real database (SQLite/PostgreSQL) using SQLAlchemy; seed inventory tables.
- Add auth for shop owners to update inventory.
- Add pagination, “in-stock” flags, and image thumbnails.

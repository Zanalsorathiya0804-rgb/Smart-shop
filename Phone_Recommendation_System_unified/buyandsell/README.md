
# Smart Shop — Buy & Sell Used Phones (HTML/CSS/JS + Python/Flask)

This starter implements a simple local marketplace for used phones. It allows users to post SELL or BUY listings, search by city/state, and contact sellers. No authentication (for demo only).

## Run locally (step-by-step)
1. Make sure Python 3.8+ is installed.
2. Unzip the downloaded folder.
3. In the project folder, install dependencies:
   ```bash
   pip install flask
   ```
4. Start the server:
   ```bash
   python app.py
   ```
   Server runs on **http://127.0.0.1:5002**.
5. Open your browser and go to **http://127.0.0.1:5002**.

## Features
- Post SELL listings (required fields: your name, contact phone, brand, model, condition, price, city, state)
- Post BUY requests (fields optional; useful to specify city/state to find nearby sellers)
- Search listings by text, city, state, and type (sell/buy)
- Contact button shows seller phone/name
- Sellers can mark their listing as SOLD (button available on sell cards)

## Files
- `app.py` — Flask backend with three endpoints:
  - `GET /api/listings` — query params `q, city, state, type, status`
  - `POST /api/listings` — create new listing (JSON or form). Required fields checked for sells.
  - `POST /api/mark_sold` — mark listing as sold by id
- `static/used.html` — frontend UI and forms
- `static/app.js` — frontend logic and requests
- `static/styles.css` — styling theme matching your other modules
- `data/listings.json` — sample listings (pre-seeded for demo)

## Next steps / improvements
- Add images upload & storage (S3 or local uploads + thumbnails)
- Add authentication for sellers (so only owners can mark sold)
- Add pagination and map-based nearby search (use geocoding + Haversine)
- Use a proper DB (SQLite/Postgres) and admin dashboards
- Email/SMS notifications when someone is interested in a listing

This is a minimal starter you can extend into a production-ready marketplace.

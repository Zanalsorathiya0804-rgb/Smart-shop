
# Smart Shop — Reviews (HTML/CSS/JS + Python/Flask)

This module allows users to submit reviews and browse reviews. It's a starter demo (no auth).

## Run locally (step-by-step)
1. Ensure Python 3.8+ is installed.
2. Unzip the downloaded folder.
3. (Optional) create & activate a virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate      # Windows PowerShell
   ```
4. Install Flask:
   ```bash
   pip install flask
   ```
5. Start the server:
   ```bash
   python app.py
   ```
   Server runs on **http://127.0.0.1:5005**.
6. Open the URL and submit/read reviews.

## API
- `GET /api/reviews` — params: `q, model, min_rating, city, sort=newest|highest`
- `POST /api/reviews` — JSON/form: `reviewer_name, rating(1-5), title, body, model, city`
- `POST /api/reviews/<id>/hide` — mark review hidden (no auth in starter)

## Next improvements
- Add authentication so only verified users can post & edit reviews.
- Add spam moderation, profanity filtering, and image attachments.
- Allow rating breakdown, upvotes/downvotes, and reporting reviews.
- Move to a real DB (SQLite/Postgres) and add admin moderation UI.

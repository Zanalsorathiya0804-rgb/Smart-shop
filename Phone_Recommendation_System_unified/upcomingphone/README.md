
# Smart Shop — Upcoming Phones (HTML/CSS/JS + Python/Flask)

This module helps users discover upcoming phone releases, see timelines, and save a reminder (demo: stores reminders locally).

## Run locally (step-by-step)
1. Ensure Python 3.8+ is installed.
2. Unzip the downloaded folder.
3. (Optional) create & activate a virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate      # Windows PowerShell
   ```
4. Install dependencies:
   ```bash
   pip install flask
   ```
5. Start the server:
   ```bash
   python app.py
   ```
   Server runs on **http://127.0.0.1:5004**.
6. Open the URL in your browser and use the search/filters. Click **Remind me** to save a reminder (demo - data saved in `data/notifications.json`).

## API
- `GET /api/upcoming` — query params: `q, brand, days, all=1, sort=soon|latest`
- `GET /api/phone/<id>` — get single phone details
- `POST /api/notify` — JSON `{ phone_id, name, contact, notes }` to store reminder
- `GET /api/notifications` — list saved reminders (admin helper)

## Data
- `data/upcoming_phones.json` — sample upcoming phones with `release_date` in `YYYY-MM-DD`
- `data/notifications.json` — saved reminder requests

## Next improvements (ideas)
- Scrape release calendars from trusted sources or use official brand RSS/press feeds to auto-update the list.
- Integrate email or SMS notification sender (e.g., SendGrid, Twilio) for actual alerts.
- Add user accounts so reminders are tied to user profiles and delivery preferences.
- Add calendar export (iCal) or browser push notifications.
- Add image thumbnails and direct links to official announcement pages.

## Integration
- To add to your Smart Shop app, merge `static/*` and `app.py` routes into your main Flask app (avoid port conflicts).
- You can run this module on the same server and mount routes under `/upcoming`.

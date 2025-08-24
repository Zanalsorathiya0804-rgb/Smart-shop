
# Smart Shop — Compare Phones (HTML/CSS/JS + Python/Flask)

A starter module to compare two phones side-by-side and get a recommendation with short reasons.

## Run locally
1. Ensure Python 3.8+ is installed.
2. Unzip the downloaded folder.
3. (Optional) create a virtualenv and activate it.
4. Install Flask:
   ```bash
   pip install flask
   ```
5. Start the server:
   ```bash
   python app.py
   ```
   Server runs on **http://127.0.0.1:5003**.
6. Open the URL and choose two phones to compare.

## How comparison works (brief)
- The server considers these specs with weights:
  - Rating (30%), Price (25%), RAM (15%), Storage (10%), Battery (12%), Camera (8%)
- Values are normalized between the two phones for fairness.
- A weighted score (0–100) is computed for each phone; the higher score is recommended.
- The response contains per-spec winners and short explanations (why one phone beats another on a spec).

## Next improvements you can add
- Allow custom weights (user chooses what matters most: price vs performance).
- Add images and sample benchmark scores (CPU/GPU) in the dataset.
- Add streaming comparison for many phones (compare top N).
- Use a proper ML model or multi-criteria decision analysis for complex choices.

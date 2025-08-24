
Smart Shop — Unified Launcher (from your uploaded project)

What I changed:
- main/index.html: added data-url attributes to each icon to point to local module servers (ports 5000-5005).
- main/script.js: updated to open the module URL in a new tab when icon clicked.
- Added run_all.sh (Linux/macOS) and run_all.bat (Windows) to start all modules in separate terminals.
- Kept original main/index.html and script.js backups as index.original.html and script.original.js in main/.
- Please run modules before clicking icons in main page.

How to run (simple):
1. Open a terminal and change directory to the project root (the folder containing 'phonefinder', 'salesprediction', etc.).
   e.g. cd "Phone Recommendation System"

2. Create and activate a virtual environment (optional but recommended):
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows PowerShell

3. Install dependencies (one-time). The modules use Flask; salesprediction also uses pandas and numpy.
   pip install flask pandas numpy

4. Start all modules with one command:
   - macOS / Linux:
       ./run_all.sh
   - Windows:
       run_all.bat
   This opens separate terminals (Windows) or background processes (macOS/Linux).

5. Open the dashboard main page in your browser:
   - Open file: main/index.html  (double-click or open in browser)
   - OR serve it over HTTP (optional) for better behavior:
       python -m http.server --directory main 8000
     Then visit: http://127.0.0.1:8000/

6. Click any icon — it will open the respective module (each module runs on its own Flask server):
   - Phone Finder: http://127.0.0.1:5000/
   - Sales Prediction: http://127.0.0.1:5001/
   - Buy & Sell: http://127.0.0.1:5002/
   - Compare: http://127.0.0.1:5003/
   - Upcoming: http://127.0.0.1:5004/
   - Reviews: http://127.0.0.1:5005/

Notes:
- If any module fails to start because the port is in use, edit that module's app.py and change the port number in app.run(...).
- If you prefer a single Flask server to serve the dashboard and all APIs, I can merge the module endpoints into one app.py — tell me if you want that and I'll prepare it.
- Backups of original main/index.html and script.js were kept in main/ as index.original.html and script.original.js.

If you'd like, I can now package the modified project into a downloadable ZIP for you. Let me know and I'll create it.

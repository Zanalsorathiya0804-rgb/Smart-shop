
# Smart Shop — Sales Prediction (HTML/CSS/JS + Python/Flask)

A plug-in module for your Smart Shop. Upload past sales, forecast future sales, and visualize the results.

## 1) Prerequisites
- Python 3.8+
- pip

## 2) Install dependencies
```bash
pip install flask pandas numpy
```

## 3) Run the server
From this folder:
```bash
python app.py
```
Then open http://127.0.0.1:5001 in your browser.

## 4) How to use
1. Prepare a CSV with columns: `date,sales` (e.g., `2024-01-01,120`)
2. Choose frequency (**D/W/M**), set horizon (e.g., 6 for months)
3. Upload your CSV **or** click **Use Sample**
4. Click **Predict**
5. See the chart and download the forecast as CSV

## 5) API
- `POST /api/predict`
  - Multipart form with `file`, `freq`, `n_periods` **or** JSON `{"sample": true, "freq": "M", "n_periods": 6}`
  - Response: `history` (date, sales, sma), `forecast` (date, yhat, lower, upper), `summary` stats
- `GET /api/sample-csv` — download sample CSV

## 6) Model (simple & fast)
- Resamples your data to the selected frequency
- Fits a **linear trend** (`y = a*t + b`)
- Forecasts future periods with **95% intervals** (±1.96 × residual std)
- Adds a **moving average** (7D / 4W / 3M) for smooth visualization

> You can swap this with ARIMA/Prophet later; this starter keeps dependencies minimal.

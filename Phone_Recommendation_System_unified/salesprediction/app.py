
from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import io, csv, math
import pandas as pd
import numpy as np
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

def load_csv_df(file_like):
    df = pd.read_csv(file_like)
    # Expect columns date,sales (case-insensitive)
    cols = {c.lower(): c for c in df.columns}
    if "date" not in cols or "sales" not in cols:
        raise ValueError("CSV must have columns: date,sales")
    df = df.rename(columns={cols["date"]:"date", cols["sales"]:"sales"})
    # Parse dates and coerce sales to numeric
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df = df.dropna(subset=["date", "sales"]).sort_values("date")
    return df

def resample_series(df, freq):
    s = df.set_index("date")["sales"].sort_index()
    if freq == "D":
        return s.resample("D").sum().fillna(0)
    if freq == "W":
        return s.resample("W").sum().fillna(0)  # weekly (Sun-anchored by default)
    if freq == "M":
        return s.resample("MS").sum().fillna(0)  # monthly (month start)
    # default daily
    return s.resample("D").sum().fillna(0)

def simple_forecast(series: pd.Series, n_periods: int):
    """
    Linear trend + Gaussian noise interval.
    y = a*t + b, intervals = +/- 1.96*std(residuals)
    """
    y = series.values.astype(float)
    t = np.arange(len(y))
    if len(y) < 2:
        a, b = 0.0, float(y.mean() if len(y) else 0.0)
        yhat_train = np.repeat(b, len(y))
        residuals = y - yhat_train
    else:
        a, b = np.polyfit(t, y, 1)
        yhat_train = a * t + b
        residuals = y - yhat_train

    # Stats for intervals & quality
    sigma = float(np.std(residuals, ddof=1)) if len(y) > 1 else 0.0
    sst = float(np.sum((y - y.mean())**2)) if len(y) > 1 else 0.0
    sse = float(np.sum((residuals)**2)) if len(y) > 1 else 0.0
    r2 = float(1.0 - sse / sst) if sst > 0 else 0.0

    # Forecast
    t_future = np.arange(len(y), len(y) + n_periods)
    yhat_future = a * t_future + b
    lower = yhat_future - 1.96 * sigma
    upper = yhat_future + 1.96 * sigma
    yhat_future = np.maximum(0, yhat_future)
    lower = np.maximum(0, lower)
    upper = np.maximum(0, upper)

    return {
        "a": float(a),
        "b": float(b),
        "sigma": sigma,
        "r2": r2,
        "train_fitted": yhat_train.tolist(),
        "future_mean": yhat_future.tolist(),
        "future_lower": lower.tolist(),
        "future_upper": upper.tolist(),
    }

def smooth(series: pd.Series, freq: str):
    if freq == "D":
        return series.rolling(7, min_periods=1).mean()
    if freq == "W":
        return series.rolling(4, min_periods=1).mean()
    if freq == "M":
        return series.rolling(3, min_periods=1).mean()
    return series

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/sample-csv")
def sample_csv():
    # Let the user download the sample
    return send_from_directory(STATIC_DIR, "sample_sales.csv", as_attachment=True)

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Accepts multipart/form-data:
      - file: CSV with columns date,sales
      - freq: D | W | M
      - n_periods: int (default based on freq)
    OR JSON body: { "sample": true, "freq": "M", "n_periods": 6 }
    Returns JSON with history + forecast arrays.
    """
    freq = "M"
    n_periods = None
    df = None

    if request.content_type and "application/json" in request.content_type:
        data = request.get_json(silent=True) or {}
        freq = (data.get("freq") or "M").upper()
        n_periods = int(data.get("n_periods") or 6)
        use_sample = bool(data.get("sample", False))
        if use_sample:
            with open(STATIC_DIR / "sample_sales.csv", "rb") as f:
                df = load_csv_df(f)
    else:
        # multipart form
        freq = (request.form.get("freq") or "M").upper()
        n_periods = int(request.form.get("n_periods") or (30 if freq == "D" else 8 if freq == "W" else 6))
        if "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            df = load_csv_df(f.stream)

    if df is None:
        # fallback to sample if nothing provided
        with open(STATIC_DIR / "sample_sales.csv", "rb") as f:
            df = load_csv_df(f)

    series = resample_series(df, freq)
    series = series.asfreq(series.index.freq or freq, fill_value=0)

    # Forecast
    if n_periods is None:
        n_periods = 6 if freq == "M" else (8 if freq == "W" else 30)
    fc = simple_forecast(series, n_periods)
    smooth_series = smooth(series, freq)

    # Build response
    history = []
    for dt, val, sma in zip(series.index, series.values, smooth_series.values):
        history.append({
            "date": dt.strftime("%Y-%m-%d"),
            "sales": float(val),
            "sma": float(sma)
        })

    # Future dates
    last = series.index[-1]
    future_index = pd.date_range(start=last + pd.tseries.frequencies.to_offset(series.index.freqstr or freq),
                                 periods=n_periods, freq=series.index.freqstr or freq)
    forecast = []
    for i, dt in enumerate(future_index):
        forecast.append({
            "date": dt.strftime("%Y-%m-%d"),
            "yhat": float(fc["future_mean"][i]),
            "lower": float(fc["future_lower"][i]),
            "upper": float(fc["future_upper"][i])
        })

    summary = {
        "n_obs": int(len(series)),
        "first_date": history[0]["date"] if history else None,
        "last_date": history[-1]["date"] if history else None,
        "freq": freq,
        "n_forecast": int(n_periods),
        "trend_slope_per_period": fc["a"],
        "trend_intercept": fc["b"],
        "r2_trend_fit": fc["r2"],
        "sigma_residual": fc["sigma"]
    }

    return jsonify({"status":"ok","history":history,"forecast":forecast,"summary":summary})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)

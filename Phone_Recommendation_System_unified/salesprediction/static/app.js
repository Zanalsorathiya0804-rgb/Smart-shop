
const $ = (sel) => document.querySelector(sel);
const fmtINR = (n) => new Intl.NumberFormat("en-IN").format(n);

let chart;

/* Build chart */
function renderChart(history, forecast) {
  const ctx = $("#chart").getContext("2d");

  const labels = [
    ...history.map(h => h.date),
    ...forecast.map(f => f.date)
  ];

  const historyData = history.map(h => h.sales);
  const smaData = history.map(h => h.sma);
  const forecastData = [
    ...Array(history.length).fill(null),
    ...forecast.map(f => f.yhat)
  ];

  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Sales", data: [...historyData, ...Array(forecast.length).fill(null)], borderWidth: 2, tension: 0.25 },
        { label: "SMA (smooth)", data: [...smaData, ...Array(forecast.length).fill(null)], borderWidth: 1, borderDash: [4,4], tension: 0.25 },
        { label: "Forecast", data: forecastData, borderWidth: 2, borderDash: [6,4], tension: 0.25 }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "top" },
        tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${fmtINR(ctx.parsed.y)}` } }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

function renderTable(forecast) {
  const wrap = $("#tableWrap");
  const rows = forecast.map(f => `<tr><td>${f.date}</td><td>${fmtINR(f.yhat.toFixed(0))}</td><td>${fmtINR(f.lower.toFixed(0))}</td><td>${fmtINR(f.upper.toFixed(0))}</td></tr>`).join("");
  wrap.innerHTML = `
    <table>
      <thead><tr><th>Date</th><th>Forecast</th><th>Lower</th><th>Upper</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function toCsv(forecast) {
  const header = "date,yhat,lower,upper";
  const lines = forecast.map(f => [f.date, f.yhat, f.lower, f.upper].join(","));
  return [header, ...lines].join("\n");
}

$("#downloadCsv").addEventListener("click", () => {
  if (!window._forecast) return;
  const csv = toCsv(window._forecast);
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "forecast.csv"; a.click();
  URL.revokeObjectURL(url);
});

/* Submit handler */
$("#predictForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData();
  const file = $("#file").files[0];
  if (file) formData.append("file", file);
  formData.append("freq", $("#freq").value);
  formData.append("n_periods", $("#n_periods").value || 6);

  const res = await fetch("/api/predict", { method: "POST", body: formData });
  const data = await res.json();
  if (data.status !== "ok") { alert("Prediction failed."); return; }

  $("#meta").textContent = `Obs: ${data.summary.n_obs} • Last: ${data.summary.last_date} • Horizon: ${data.summary.n_forecast} • R² (trend): ${Number(data.summary.r2_trend_fit).toFixed(2)}`;
  renderChart(data.history, data.forecast);
  renderTable(data.forecast);
  window._forecast = data.forecast;
});

/* Sample button */
$("#sampleBtn").addEventListener("click", async () => {
  const payload = { sample: true, freq: $("#freq").value, n_periods: Number($("#n_periods").value || 6) };
  const res = await fetch("/api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  const data = await res.json();
  if (data.status !== "ok") { alert("Prediction failed."); return; }

  $("#meta").textContent = `Obs: ${data.summary.n_obs} • Last: ${data.summary.last_date} • Horizon: ${data.summary.n_forecast} • R² (trend): ${Number(data.summary.r2_trend_fit).toFixed(2)}`;
  renderChart(data.history, data.forecast);
  renderTable(data.forecast);
  window._forecast = data.forecast;
});

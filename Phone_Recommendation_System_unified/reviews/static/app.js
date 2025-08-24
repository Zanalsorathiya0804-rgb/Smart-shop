
const $ = s => document.querySelector(s);

async function fetchReviews(params={}){
  const url = new URL(location.origin + "/api/reviews");
  Object.entries(params).forEach(([k,v])=>{ if (v !== undefined && v !== null && String(v).trim() !== "") url.searchParams.set(k, v); });
  const res = await fetch(url);
  return res.json();
}

function starHTML(n){
  n = Number(n) || 0;
  return "★".repeat(n) + "☆".repeat(5-n);
}

function reviewCard(r){
  const div = document.createElement("div");
  div.className = "review-card";
  div.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:flex-start">
      <div>
        <strong>${r.title || (r.model ? r.model + " review" : "Review")}</strong>
        <div class="review-meta">
          <div>${r.reviewer_name || "Anonymous"} • <span class="small">${r.model || ""}</span></div>
          <div class="stars">${starHTML(r.rating)}</div>
        </div>
      </div>
      <div class="small muted">${new Date(r.created_at).toLocaleString()}</div>
    </div>
    <p style="margin-top:8px">${r.body}</p>
    <div class="small muted">City: ${r.city || "—"}</div>
  `;
  return div;
}

async function renderReviews(params={}){
  const data = await fetchReviews(params);
  $("#reviewsWrap").innerHTML = "";
  $("#stats").textContent = data.total ? `(${data.total} reviews • avg ${data.avg_rating || "-"})` : "(no reviews yet)";
  if (data.total === 0) {
    $("#reviewsWrap").innerHTML = `<div class="muted">No reviews yet — be the first to write one!</div>`;
    return;
  }
  data.results.forEach(r => $("#reviewsWrap").appendChild(reviewCard(r)));
}

document.addEventListener("DOMContentLoaded", ()=>{
  renderReviews();

  $("#reviewForm").addEventListener("submit", async (e)=>{
    e.preventDefault();
    const form = new FormData(e.target);
    const payload = {};
    for (const [k,v] of form.entries()) payload[k]=v;
    if (!payload.rating) return alert("Please choose a rating 1-5.");
    if (!payload.body || payload.body.trim().length < 5) return alert("Please write a short review (min 5 characters).");
    const res = await fetch("/api/reviews", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
    const data = await res.json();
    if (data.status === "ok") {
      alert("Thanks! Your review was posted.");
      e.target.reset();
      renderReviews();
    } else {
      alert("Failed: " + (data.message || "error"));
    }
  });

  $("#filterForm").addEventListener("submit", (e)=>{
    e.preventDefault();
    const q = $("#q").value.trim();
    const model = $("#filterModel").value.trim();
    const minRating = $("#minRating").value;
    const params = {};
    if (q) params.q = q;
    if (model) params.model = model;
    if (minRating) params.min_rating = minRating;
    renderReviews(params);
  });

  $("#clearBtn").addEventListener("click", ()=>{
    $("#q").value = ""; $("#filterModel").value = ""; $("#minRating").value = "";
    renderReviews();
  });
});

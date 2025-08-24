
const $ = (s) => document.querySelector(s);

async function fetchListings(params={}) {
  const url = new URL(location.origin + "/api/listings");
  Object.entries(params).forEach(([k,v]) => { if (v) url.searchParams.set(k, v); });
  const res = await fetch(url);
  return res.json();
}

function el(html) { const d=document.createElement("div"); d.innerHTML=html.trim(); return d.firstChild; }

function listingCard(l) {
  const div = document.createElement("div");
  div.className = "listing-card";
  div.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center">
      <strong>${l.brand || ""} ${l.model || ""} <span class="muted">(${l.type})</span></strong>
      <span class="muted">${new Date(l.posted_at).toLocaleString()}</span>
    </div>
    <div class="listing-meta">
      <div>Condition: ${l.condition || "-"}</div>
      <div>Price: ${l.price ? ("₹"+Number(l.price).toLocaleString()) : "-"}</div>
      <div>Location: ${l.city || "-"}, ${l.state || "-"}</div>
      <div>Seller: ${l.seller_name || "-"}</div>
      <div>Contact: ${l.contact_phone || "-"}</div>
    </div>
    <p style="margin:10px 0">${l.description || ""}</p>
    <div style="display:flex; gap:8px; flex-wrap:wrap;">
      ${l.type === "sell" ? `<button class="btn primary contactBtn" data-id="${l.id}">Contact Seller</button>` : `<button class="btn contactBtn" data-id="${l.id}">I'm Interested</button>`}
      ${l.type === "sell" ? `<button class="btn markSold" data-id="${l.id}">Mark as Sold</button>` : ""}
    </div>
  `;

  // events
  const contactBtn = div.querySelector(".contactBtn");
  contactBtn.addEventListener("click", () => {
    alert(`Contact Info:\\nName: ${l.seller_name || "—"}\\nPhone: ${l.contact_phone || "—"}`);
  });
  const markBtn = div.querySelector(".markSold");
  if (markBtn) {
    markBtn.addEventListener("click", async () => {
      if (!confirm("Mark this listing as SOLD? (This cannot be undone)")) return;
      const res = await fetch("/api/mark_sold", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({id: l.id})});
      const data = await res.json();
      if (data.status === "ok") {
        alert("Marked as sold.");
        loadListings();
      } else alert("Failed: "+(data.message || "error"));
    });
  }
  return div;
}

async function loadListings() {
  const q = $("#q").value.trim();
  const city = $("#filterCity").value.trim();
  const state = $("#filterState").value.trim();
  const type = $("#filterType").value;
  const params = {};
  if (q) params.q = q;
  if (city) params.city = city;
  if (state) params.state = state;
  if (type) params.type = type;
  params.status = "available";
  const res = await fetchListings(params);
  const wrap = $("#listingsWrap");
  wrap.innerHTML = "";
  if (res.total === 0) {
    wrap.innerHTML = `<div class="muted">No listings found. Try clearing filters or post a new listing.</div>`;
    return;
  }
  res.results.forEach(l => wrap.appendChild(listingCard(l)));
}

/* Form toggles */
$("#sellBtn").addEventListener("click", () => {
  $("#formCard").style.display = "block";
  $("#formTitle").textContent = "Sell a phone";
  $("#type").value = "sell";
  // required for selling
  $("#seller_name").required = true;
  $("#contact_phone").required = true;
});

$("#buyBtn").addEventListener("click", () => {
  $("#formCard").style.display = "block";
  $("#formTitle").textContent = "Looking to Buy";
  $("#type").value = "buy";
  // buyer fields optional
  $("#seller_name").required = false;
  $("#contact_phone").required = false;
});

$("#cancelForm").addEventListener("click", () => {
  $("#formCard").style.display = "none";
  $("#listingForm").reset();
});

/* Submit listing */
$("#listingForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const payload = {};
  for (const [k,v] of form.entries()) payload[k]=v;
  // convert price
  if (payload.price) payload.price = Number(payload.price || 0);
  const res = await fetch("/api/listings", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
  const data = await res.json();
  if (data.status === "ok") {
    alert("Listing posted successfully.");
    $("#listingForm").reset();
    $("#formCard").style.display = "none";
    loadListings();
  } else {
    alert("Failed to post: "+(data.message||"error"));
  }
});

/* Search form */
$("#searchForm").addEventListener("submit", (e) => { e.preventDefault(); loadListings(); });
$("#clearSearch").addEventListener("click", () => { $("#q").value=""; $("#filterCity").value=""; $("#filterState").value=""; $("#filterType").value=""; loadListings(); });

/* initial load */
document.addEventListener("DOMContentLoaded", () => {
  loadListings();
});


/* Shared helpers */
const $ = (sel) => document.querySelector(sel);
const $all = (sel) => Array.from(document.querySelectorAll(sel));
const fmtINR = (n) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

/* ====== Phone Finder page logic ====== */
async function fetchPhones(params = {}) {
  const url = new URL(location.origin + "/api/phones");
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && String(v).trim() !== "") url.searchParams.set(k, v);
  });
  const res = await fetch(url);
  return res.json();
}

function phoneCard(p) {
  const div = document.createElement("div");
  div.className = "phone-card";
  const title = `${p.brand} ${p.model}`;

  div.innerHTML = `
    <h3>${title}</h3>
    <div class="phone-meta">
      <div>RAM: ${p.ram_gb} GB</div>
      <div>Storage: ${p.storage_gb} GB</div>
      <div>Battery: ${p.battery_mah} mAh</div>
      <div>Rating: ${p.rating}★</div>
    </div>
    <div class="price">${fmtINR(p.price)}</div>
    <div class="card-actions">
      <button class="btn primary buy-btn" data-id="${p.id}" data-brand="${p.brand}">Buy Now</button>
      <span class="muted">ID: ${p.id}</span>
    </div>
  `;

  div.querySelector(".buy-btn").addEventListener("click", () => {
    const id = p.id;
    const brand = encodeURIComponent(p.brand);
    window.location.href = `/shops.html?model_id=${encodeURIComponent(id)}&brand=${brand}`;
  });

  return div;
}

async function initFinder() {
  if (!document.getElementById("filterForm")) return; // not on this page
  const brandSelect = document.getElementById("brand");
  const resultsEl = document.getElementById("results");
  const countEl = document.getElementById("resultsCount");

  // Load initial to populate brands
  const initial = await fetchPhones();
  const brands = Array.from(new Set(initial.results.map(p => p.brand))).sort();
  brands.forEach(b => {
    const opt = document.createElement("option");
    opt.value = b;
    opt.textContent = b;
    brandSelect.appendChild(opt);
  });

  const render = (data) => {
    resultsEl.innerHTML = "";
    data.results.forEach(p => resultsEl.appendChild(phoneCard(p)));
    countEl.textContent = `${data.total} phone(s) found`;
  };

  render(initial);

  document.getElementById("filterForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const params = {
      q: document.getElementById("q").value,
      brand: document.getElementById("brand").value,
      min_price: document.getElementById("min_price").value,
      max_price: document.getElementById("max_price").value,
      ram_min: document.getElementById("ram_min").value,
      storage_min: document.getElementById("storage_min").value,
      sort: document.getElementById("sort").value
    };
    const data = await fetchPhones(params);
    render(data);
  });

  document.getElementById("clearBtn").addEventListener("click", async () => {
    ["q","brand","min_price","max_price","ram_min","storage_min","sort"].forEach(id => {
      const el = document.getElementById(id);
      if (el.tagName === "SELECT") el.selectedIndex = 0; else el.value = "";
    });
    const data = await fetchPhones();
    render(data);
  });
}

/* ====== Shops page logic ====== */
async function initShops() {
  if (!document.getElementById("shopForm")) return; // not on this page
  const params = new URLSearchParams(location.search);
  const modelId = params.get("model_id");
  const brand = params.get("brand");

  // Show selected phone details
  const phoneRes = await fetchPhones({ model_id: modelId });
  const phone = phoneRes.results[0];
  const selectedPhoneEl = document.getElementById("selectedPhone");
  if (phone) {
    selectedPhoneEl.textContent = `Selected: ${phone.brand} ${phone.model} — ${fmtINR(phone.price)} (RAM ${phone.ram_gb} GB, Storage ${phone.storage_gb} GB)`;
  } else {
    selectedPhoneEl.textContent = `Selected Model ID: ${modelId}`;
  }

  const resultsEl = document.getElementById("shopResults");
  const countEl = document.getElementById("shopCount");

  const renderShops = (data) => {
    resultsEl.innerHTML = "";
    if (data.total === 0) {
      resultsEl.innerHTML = `<div class="shop-item">No shops found for your filters. Try another nearby city or state.</div>`;
      countEl.textContent = `0 shop(s) found`;
      return;
    }
    data.results.forEach(s => {
      const div = document.createElement("div");
      div.className = "shop-item";
      div.innerHTML = `
        <strong>${s.name}</strong><br/>
        ${s.address}, ${s.city}, ${s.state} - ${s.pincode}<br/>
        Brands: ${s.phone_brands.join(", ")}<br/>
        Phone: ${s.phone}<br/>
        Hours: ${s.opening_hours}
      `;
      resultsEl.appendChild(div);
    });
    countEl.textContent = `${data.total} shop(s) found`;
  };

  document.getElementById("shopForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const city = document.getElementById("city").value;
    const state = document.getElementById("state").value;
    const url = new URL(location.origin + "/api/shops");
    if (city) url.searchParams.set("city", city);
    if (state) url.searchParams.set("state", state);
    if (modelId) url.searchParams.set("model_id", modelId); else if (brand) url.searchParams.set("brand", brand);
    const res = await fetch(url);
    const data = await res.json();
    renderShops(data);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initFinder();
  initShops();
});

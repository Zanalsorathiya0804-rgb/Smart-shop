
const $ = s => document.querySelector(s);

async function fetchUpcoming(params={}){
  const url = new URL(location.origin + "/api/upcoming");
  Object.entries(params).forEach(([k,v])=>{ if (v !== undefined && v !== null && String(v).trim() !== "") url.searchParams.set(k, v); });
  const res = await fetch(url);
  return res.json();
}

function daysUntil(dateStr){
  if (!dateStr) return null;
  const today = new Date(); today.setHours(0,0,0,0);
  const d = new Date(dateStr + "T00:00:00");
  const diff = Math.ceil((d - today)/(1000*60*60*24));
  return diff;
}

function phoneCard(p){
  const div = document.createElement("div");
  div.className = "phone-card";
  const days = p._days_until;
  const soonText = (days===null) ? "TBA" : (days < 0 ? "Already released" : (days===0 ? "Releases today" : `${days} day(s)`));
  div.innerHTML = `
    <div class="left">
      <strong>${p.brand} ${p.model}</strong>
      <div class="small">${p.description || ""}</div>
      <div class="small">Release date: ${p.release_date || "TBA"} • ${soonText}</div>
      <div class="small">Announced by: ${p.announced_by || "—"} • Pre-order: ${p.pre_order_date || "—"}</div>
    </div>
    <div class="right">
      <button class="btn primary remindBtn" data-id="${p.id}">Remind me</button>
      <div style="height:8px"></div>
      <a class="btn" href="#" data-id="${p.id}" onclick="viewDetails(event)">Details</a>
    </div>
  `;
  div.querySelector(".remindBtn").addEventListener("click", () => openReminder(p));
  return div;
}

function viewDetails(e){
  e.preventDefault();
  const id = e.currentTarget.getAttribute("data-id");
  // navigate to detail page? For simplicity, fetch phone and alert details
  fetch(`/api/phone/${id}`).then(r=>r.json()).then(data=>{
    if (data.status === "ok") {
      const p = data.phone;
      alert(`${p.brand} ${p.model}\n\nRelease: ${p.release_date || "TBA"}\nPrice: ${p.price || "TBD"}\n\n${p.description || ""}\n\nNotes: ${p.notes || ""}`)
    } else alert("Phone not found");
  });
}

function openReminder(p){
  $("#reminderModal").style.display = "flex";
  $("#phone_id").value = p.id;
  $("#modalTitle").textContent = `Remind me: ${p.brand} ${p.model}`;
}

function closeModal(){
  $("#reminderModal").style.display = "none";
  $("#reminderForm").reset();
}

async function saveReminder(e){
  e.preventDefault();
  const form = new FormData(e.target);
  const payload = {};
  for (const [k,v] of form.entries()) payload[k]=v;
  const res = await fetch("/api/notify", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
  const data = await res.json();
  if (data.status === "ok") {
    alert("Reminder saved. We'll keep it on file (demo).");
    closeModal();
  } else alert("Failed: "+(data.message||"error"));
}

async function renderResults(params={}){
  const data = await fetchUpcoming(params);
  $("#results").innerHTML = "";
  $("#count").textContent = `(${data.total})`;
  if (data.total === 0) {
    $("#results").innerHTML = `<div class="small">No upcoming phones found. Try widening the days range or clear filters.</div>`;
    return;
  }
  data.results.forEach(p => $("#results").appendChild(phoneCard(p)));
}

function populateBrands(phones){
  const set = new Set(phones.map(p=>p.brand).filter(Boolean));
  const sel = $("#brand");
  set.forEach(b => {
    const o = document.createElement("option"); o.value = b; o.textContent = b; sel.appendChild(o);
  });
}

document.addEventListener("DOMContentLoaded", async ()=>{
  // initial load
  const urlParams = new URLSearchParams(location.search);
  const showAll = urlParams.get("all");
  const params = {};
  if (showAll === "1") params.all = "1";
  const initial = await fetchUpcoming(params);
  populateBrands(initial.results);
  renderResults(params);

  $("#searchForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const q = $("#q").value.trim();
    const brand = $("#brand").value;
    const days = $("#days").value;
    const sort = $("#sort").value;
    const p = {};
    if (q) p.q = q;
    if (brand) p.brand = brand;
    if (days) p.days = days;
    if (sort) p.sort = sort;
    renderResults(p);
  });

  $("#clearBtn").addEventListener("click", () => {
    $("#q").value = ""; $("#brand").selectedIndex = 0; $("#days").value = 365; $("#sort").value = "soon";
    renderResults({});
  });

  $("#closeModal").addEventListener("click", closeModal);
  $("#reminderForm").addEventListener("submit", saveReminder);
});

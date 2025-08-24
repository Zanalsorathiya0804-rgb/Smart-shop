
const $ = s => document.querySelector(s);
const leftSelect = $("#leftSelect");
const rightSelect = $("#rightSelect");
let phones = [];

async function loadPhones() {
  const res = await fetch("/api/phones");
  const data = await res.json();
  phones = data.results;
  leftSelect.innerHTML = `<option value="">-- Select phone A --</option>` + phones.map(p=>`<option value="${p.id}">${p.brand} ${p.model}</option>`).join("");
  rightSelect.innerHTML = `<option value="">-- Select phone B --</option>` + phones.map(p=>`<option value="${p.id}">${p.brand} ${p.model}</option>`).join("");
}

function renderPhoneCard(target, p) {
  if (!p) { target.innerHTML = "<div class='muted'>No phone selected</div>"; return; }
  target.innerHTML = `
    <h3>${p.brand} ${p.model}</h3>
    <div class="muted">Price: ₹${Number(p.price).toLocaleString()}</div>
    <div style="margin-top:8px">
      <div>Rating: ${p.rating} ★</div>
      <div>RAM: ${p.ram_gb} GB</div>
      <div>Storage: ${p.storage_gb} GB</div>
      <div>Battery: ${p.battery_mah} mAh</div>
      <div>Camera: ${p.camera_mp} MP</div>
      <div>Display: ${p.display_inch} ″</div>
    </div>
  `;
}

function renderSpecsTable(per_spec, left, right) {
  const rows = per_spec.map(ps => {
    const leftClass = ps.winner === "left" ? "winner" : "";
    const rightClass = ps.winner === "right" ? "winner" : "";
    return `<tr>
      <td>${ps.label}</td>
      <td class="${leftClass}">${ps.left_value}</td>
      <td class="${rightClass}">${ps.right_value}</td>
    </tr>`;
  }).join("");
  $("#specsTable").innerHTML = `<table><thead><tr><th>Spec</th><th>Phone A</th><th>Phone B</th></tr></thead><tbody>${rows}</tbody></table>`;
}

async function doCompare(id1, id2) {
  const res = await fetch("/api/compare", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({id1, id2}) });
  const data = await res.json();
  if (data.status !== "ok") { alert("Compare failed: "+(data.message||"")); return; }
  // show compare card
  $("#compareCard").style.display = "block";
  renderPhoneCard($("#leftCard"), data.left);
  renderPhoneCard($("#rightCard"), data.right);
  renderSpecsTable(data.per_spec, data.left, data.right);
  $("#recommendation").textContent = data.summary;
  const reasons = $("#reasons");
  reasons.innerHTML = data.explanations.map(r => `<li>${r}</li>`).join("");
  // scroll into view
  $("#compareCard").scrollIntoView({behavior:"smooth", block:"start"});
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadPhones();
  $("#compareBtn").addEventListener("click", async () => {
    const id1 = leftSelect.value;
    const id2 = rightSelect.value;
    if (!id1 || !id2) return alert("Select two phones to compare.");
    if (id1 === id2) return alert("Choose two different phones.");
    await doCompare(id1, id2);
  });
  $("#swapBtn").addEventListener("click", () => {
    const a = leftSelect.value, b = rightSelect.value;
    leftSelect.value = b; rightSelect.value = a;
  });
  $("#clearBtn").addEventListener("click", () => {
    leftSelect.selectedIndex = 0; rightSelect.selectedIndex = 0; $("#compareCard").style.display="none";
  });
});

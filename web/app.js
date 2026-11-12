// Axon web app - plain JS, no build step. Reads the NEAR contract through the app backend.
const $ = (s) => document.querySelector(s);
const view = $("#view");
const COLORS = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)", "var(--s5)"];
const YOCTO = 1e24;
let CONFIG = null;

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const near = (y, d = 4) => (Number(y) / YOCTO).toFixed(d);
const short = (a) => (a.split(".").length > 2 ? a.split(".")[0] : a);
const txLink = (h) => (h ? `<a class="mono" target="_blank" href="${CONFIG.explorer}/txns/${h}">${h.slice(0, 8)}…</a>` : "");
const acctLink = (a) => `<a target="_blank" title="${esc(a)}" href="${CONFIG.explorer}/address/${a}">${esc(short(a))}</a>`;

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "content-type": "application/json" }, ...opts });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body.detail || r.statusText);
  return body;
}

// Example models shown on the explore page so the platform's range is visible; clearly marked, not live.
const EXAMPLES = [
  { name: "Scam Detector", domain: "security", text: "Exchanges and wallets pool flagged accounts and scam reports without exposing users." },
  { name: "Drug Safety", domain: "pharma", text: "Labs pool private compound test results to predict toxicity earlier." },
  { name: "Contract Helper", domain: "legal", text: "Law firms pool private contracts to train a drafting assistant they co-own." },
];

// ------------------------------------------------------------------ pages

async function pageModels() {
  const models = await api("/api/models");
  view.innerHTML = `
    <section class="hero">
      <h1>Train AI on your private data.<br>Own what it becomes.</h1>
      <p>Big Tech trains AI on your data for free. On Axon, people and organisations train models together
      without ever sharing their data, own a share of the model based on how much they improved it, and get paid every time it is used.</p>
    </section>
    <h2>Models being built</h2>
    <div class="grid">
      ${models.map((m) => modelCard(m)).join("") || `<p class="muted">No models yet. <a href="#/create">Create one</a>.</p>`}
      ${EXAMPLES.map((e) => `<div class="card soon"><span class="tag">${esc(e.domain)} · example</span><h3>${esc(e.name)}</h3><p class="muted small">${esc(e.text)}</p></div>`).join("")}
    </div>`;
}

function modelCard(m) {
  const improved = m.base_eval_loss_milli && m.eval_loss_milli ? ((1 - m.eval_loss_milli / m.base_eval_loss_milli) * 100).toFixed(1) : null;
  return `<a class="card" href="#/model/${m.id}">
    <span class="tag">${esc(m.domain)} · live</span>
    <h3>${esc(m.name)}</h3>
    <p class="muted small">${esc(m.description)}</p>
    <div class="small">${m.contributors.length} owners · ${m.rounds} rounds · ${m.queries} paid queries${improved ? ` · ${improved}% better` : ""}</div>
  </a>`;
}

async function pageModel(id) {
  const m = await api(`/api/models/${id}`);
  const total = Number(m.total_shares) || 1;
  const owners = m.contributors.slice().sort((a, b) => Number(b.shares) - Number(a.shares));
  // Same formula as the contract's earnings_of: pending + shares * acc_per_share / 1e9 - reward_debt
  const acc = BigInt(m.acc_per_share);
  const earnings = owners.map((c) => (BigInt(c.pending) + (BigInt(c.shares) * acc) / 1000000000n - BigInt(c.reward_debt)).toString());
  const vault = CONFIG.vault;
  const keyOk = vault && vault.combiner_key === m.combiner_key && vault.code_hash === m.combiner_code_hash;

  view.innerHTML = `
    <a href="#/" class="small">← All models</a>
    <section class="hero" style="margin-top:12px"><h1>${esc(m.name)}</h1><p>${esc(m.description)}</p></section>
    <div class="kpis">
      <div class="kpi"><div class="v">${m.contributors.length}</div><div class="l">Owners</div></div>
      <div class="kpi"><div class="v">${m.rounds}</div><div class="l">Training rounds</div></div>
      <div class="kpi"><div class="v">${m.base_eval_loss_milli ? (m.base_eval_loss_milli / 1000).toFixed(3) + " → " + (m.eval_loss_milli / 1000).toFixed(3) : "-"}</div><div class="l">Hidden-test loss</div></div>
      <div class="kpi"><div class="v">${m.queries}</div><div class="l">Paid queries</div></div>
      <div class="kpi"><div class="v">${near(m.total_revenue, 3)} Ⓝ</div><div class="l">Paid to owners</div></div>
    </div>

    <div class="two">
      <div class="card">
        <h3>Who owns this model</h3>
        <p class="muted small">Shares = how much each contributor's private data improved the model on a hidden test. Data that doesn't help earns nothing.</p>
        <div class="bar">${owners.map((c, i) => `<span style="width:${(100 * Number(c.shares)) / total}%;background:${COLORS[i % 5]}" title="${esc(c.account)}"></span>`).join("")}</div>
        <table>
          <tr><th>Owner</th><th class="num">Share</th><th class="num">Last improvement</th><th class="num">Earned</th></tr>
          ${owners.map((c, i) => `<tr>
            <td><span class="dot" style="background:${COLORS[i % 5]}"></span>${acctLink(c.account)}</td>
            <td class="num ${Number(c.shares) === 0 ? "zero" : ""}">${((100 * Number(c.shares)) / total).toFixed(1)}%</td>
            <td class="num">${(Number(c.last_improvement_micro) / 1e6).toFixed(4)}</td>
            <td class="num">${near(earnings[i], 5)} Ⓝ</td></tr>`).join("")}
        </table>
      </div>
      <div class="card">
        <h3>Ask this model</h3>
        <p class="muted small">Your question goes only to the sealed vault. Each paid question is split among the owners on-chain.</p>
        <textarea id="q" placeholder="e.g. What are the early signs of type 2 diabetes?"></textarea>
        <label>Pay with</label>
        <select id="asset">
          <option value="testnet">Testnet NEAR (demo, instant)</option>
          ${CONFIG.tokens.map((t) => `<option value="${t.id}">${esc(t.label)} · via NEAR Intents</option>`).join("")}
        </select>
        <div id="refund-wrap" style="display:none"><label>Your refund address on that chain</label><input id="refund" placeholder="0x… / So1… / bc1…"></div>
        <div class="row"><button id="askbtn">Pay ${near(m.query_price, 3)} Ⓝ and ask</button></div>
        <div id="askout"></div>
      </div>
    </div>

    <h2>Training rounds</h2>
    <div class="two">
      <div class="card chart">${lossChart(m)}</div>
      <div class="card">
        <table><tr><th>Round</th><th class="num">Test loss</th><th class="num">Shares minted</th><th>Excluded</th></tr>
        ${m.rounds_detail.slice().reverse().map((r) => `<tr><td>#${r.round}</td><td class="num">${(r.eval_loss_milli / 1000).toFixed(3)}</td>
          <td class="num">${r.results.reduce((s, x) => s + Number(x.shares), 0).toLocaleString()}</td>
          <td class="small">${r.results.filter((x) => Number(x.shares) === 0).map((x) => esc(short(x.account))).join(", ") || "-"}</td></tr>`).join("") || `<tr><td colspan="4" class="muted">No rounds yet.</td></tr>`}
        </table>
      </div>
    </div>

    <h2>Why you can trust the numbers</h2>
    <div class="card small">
      <p>Round results are signed by the vault's key <code>${esc(m.combiner_key.slice(0, 16))}…</code>, bound to vault code hash <code>${esc(m.combiner_code_hash.slice(0, 16))}…</code>.
      The NEAR contract rejects any result not signed by that key, any replayed round, and any payout to an account that didn't register on-chain.</p>
      <p>${keyOk ? "✅ The running vault's key and code hash match what is registered on-chain." : "⚠️ The running vault does not match the on-chain registration."}
      Attestation mode: <b>${esc(vault?.attestation?.mode || "unknown")}</b>. ${esc(vault?.attestation?.note || "")}</p>
      <p>Base model: <code>${esc(m.base_model)}</code> · Compute providers are paid a fixed fee per round (${near(m.compute_fee, 3)} Ⓝ), not ownership. Training budget left: ${near(m.budget, 3)} Ⓝ.</p>
    </div>`;

  $("#asset").onchange = (e) => ($("#refund-wrap").style.display = e.target.value === "testnet" ? "none" : "block");
  $("#askbtn").onclick = () => ask(m);
}

function lossChart(m) {
  const pts = [{ round: 0, loss: m.rounds_detail.length ? (m.base_eval_loss_milli / 1000) : null }, ...m.rounds_detail.map((r) => ({ round: r.round, loss: r.eval_loss_milli / 1000 }))].filter((p) => p.loss != null);
  if (pts.length < 2) return `<p class="muted small">The loss curve appears after the first round.</p>`;
  const W = 400, H = 180, P = 30;
  const ls = pts.map((p) => p.loss), lo = Math.min(...ls), hi = Math.max(...ls), span = hi - lo || 1;
  const x = (i) => P + (i * (W - 2 * P)) / (pts.length - 1);
  const y = (l) => 26 + ((hi - l) / span) * (H - 56);
  const path = pts.map((p, i) => `${i ? "L" : "M"}${x(i)},${y(p.loss)}`).join(" ");
  return `<h3>Hidden-test loss (lower is better)</h3><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Loss per round">
    <path d="${path}" fill="none" stroke="var(--accent)" stroke-width="2.5"/>
    ${pts.map((p, i) => `<circle cx="${x(i)}" cy="${y(p.loss)}" r="4" fill="var(--accent)"/><text x="${x(i)}" y="${H - 6}" text-anchor="middle">${i === 0 ? "base" : "#" + p.round}</text><text x="${x(i)}" y="${y(p.loss) - 9}" text-anchor="middle">${p.loss.toFixed(3)}</text>`).join("")}
  </svg>`;
}

async function ask(m) {
  const q = $("#q").value.trim();
  const out = $("#askout");
  const btn = $("#askbtn");
  if (!q) return (out.innerHTML = `<div class="notice warn">Type a question first.</div>`);
  const asset = $("#asset").value;
  btn.disabled = true;
  try {
    if (asset === "testnet") {
      out.innerHTML = `<p class="small"><span class="spin"></span>Paying on-chain, then asking the vault…</p>`;
      const r = await api("/api/ask-testnet", { method: "POST", body: JSON.stringify({ model_id: m.id, question: q }) });
      out.innerHTML = `<div class="answer">${esc(r.answer)}</div><p class="small muted">Paid by ${acctLink(r.payer)} · tx ${txLink(r.payment_tx)} · not medical advice</p>`;
      setTimeout(() => pageModel(m.id), 2500);
    } else {
      const refund = $("#refund").value.trim();
      if (!refund) throw new Error("Enter a refund address on the chain you're paying from.");
      out.innerHTML = `<p class="small"><span class="spin"></span>Getting a NEAR Intents quote…</p>`;
      const r = await api("/api/quote", { method: "POST", body: JSON.stringify({ model_id: m.id, origin_asset: asset, refund_to: refund, question: q, dry: false }) });
      const qt = r.quote;
      out.innerHTML = `<div class="notice">Send exactly <b>${esc(qt.amountInFormatted)}</b> (${esc(CONFIG.tokens.find((t) => t.id === asset).label)}, ≈ $${Number(qt.amountInUsd).toFixed(2)}) to<br><code>${esc(qt.depositAddress)}</code><br>
        NEAR Intents converts it to ${near(m.query_price, 3)} Ⓝ for the owners. Your answer appears here once it settles (~${qt.timeEstimate}s).</div><p class="small" id="ostate"><span class="spin"></span>Waiting for your deposit…</p>`;
      pollOrder(qt.depositAddress, m.id);
    }
  } catch (e) {
    out.innerHTML = `<div class="notice warn">${esc(e.message)}</div>`;
  } finally {
    btn.disabled = false;
  }
}

async function pollOrder(dep, modelId) {
  try {
    const o = await api(`/api/orders/${dep}`);
    if (o.state === "answered") {
      $("#askout").innerHTML = `<div class="answer">${esc(o.answer)}</div><p class="small muted">Paid via NEAR Intents (${esc(o.source)}) · tx ${txLink(o.payment_tx)}</p>`;
      return;
    }
    const s = $("#ostate");
    if (s) s.innerHTML = `<span class="spin"></span>Intents status: ${esc(o.intents_status || "waiting")}`;
  } catch (e) { /* keep polling */ }
  if (location.hash === `#/model/${modelId}`) setTimeout(() => pollOrder(dep, modelId), 5000);
}

function pageContribute() {
  view.innerHTML = `
    <section class="hero"><h1>Contribute your data. Keep it.</h1>
    <p>Your data never leaves your machine. You train the shared model locally and send only a sealed, signed update that only the vault can open.</p></section>
    <div class="two">
      <div class="card"><ol class="steps">
        <li><b>Join the model on NEAR.</b> Your account registers a device key on-chain, so nobody can submit updates in your name.</li>
        <li><b>Train locally.</b> The current shared model is fine-tuned on your private file, on your machine.</li>
        <li><b>Send a sealed update.</b> Only the adapter (what the model learned) is sent, encrypted to the vault and signed by your device.</li>
        <li><b>Get scored.</b> The vault measures how much your update improved the model on a hidden test. Junk or harmful data scores zero and is left out.</li>
        <li><b>Own and earn.</b> The score becomes your ownership share on NEAR. Every paid question pays you automatically.</li>
      </ol></div>
      <div class="card"><h3>Run it</h3>
<pre>python -m axon contribute \\
  --model 0 \\
  --account you.testnet \\
  --data my_private_data.jsonl</pre>
      <p class="small muted">Data format: one JSON object per line, <code>{"q": "...", "a": "..."}</code>. The file is read locally and never uploaded.</p></div>
    </div>`;
}

async function pageEarnings() {
  const saved = localStorageGet("axon.account") || "";
  view.innerHTML = `
    <section class="hero"><h1>Your earnings</h1><p>Your ownership in every model, and what it has earned you.</p></section>
    <div class="card"><label>NEAR account</label><div class="row" style="margin-top:0"><input id="acct" value="${esc(saved)}" placeholder="alice.testnet" style="flex:1"><button id="go">Show</button></div><div id="eout"></div></div>`;
  const run = async () => {
    const a = $("#acct").value.trim();
    if (!a) return;
    localStorageSet("axon.account", a);
    $("#eout").innerHTML = `<p class="small"><span class="spin"></span>Reading NEAR…</p>`;
    const rows = await api(`/api/earnings/${encodeURIComponent(a)}`);
    $("#eout").innerHTML = rows.length ? `<table style="margin-top:12px"><tr><th>Model</th><th class="num">Ownership</th><th class="num">Withdrawable</th></tr>
      ${rows.map((r) => `<tr><td><a href="#/model/${r.model_id}">${esc(r.name)}</a></td><td class="num">${((100 * Number(r.shares)) / (Number(r.total_shares) || 1)).toFixed(1)}%</td><td class="num">${near(r.earnings, 5)} Ⓝ</td></tr>`).join("")}</table>
      <p class="small muted">Withdraw with <code>python -m axon withdraw --model &lt;id&gt; --account ${esc(a)}</code>.</p>` : `<p class="muted">This account doesn't own a share of any model yet.</p>`;
  };
  $("#go").onclick = run;
  if (saved) run();
}

function pageCreate() {
  view.innerHTML = `
    <section class="hero"><h1>Start a model</h1><p>Pick an open base model and a topic, fund the compute budget, and invite people or organisations with private data to build it with you.</p></section>
    <div class="card"><pre>python -m axon create-model \\
  --creator you.testnet \\
  --name "Sleep Coach" --domain health \\
  --description "Trained on wearable sleep data from its owners" \\
  --price 0.01 --compute-fee 0.05 --budget 0.5</pre>
    <p class="small muted">The model is bound on-chain to the vault's signing key and code hash. Compute providers are paid a fixed fee per round from the budget; ownership goes only to data contributors.</p></div>`;
}

function localStorageGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function localStorageSet(k, v) { try { localStorage.setItem(k, v); } catch { /* ignore */ } }

// ------------------------------------------------------------------ router

async function route() {
  const h = location.hash || "#/";
  document.querySelectorAll("nav a").forEach((a) => a.classList.toggle("on", a.getAttribute("href") === h));
  view.innerHTML = `<p class="muted"><span class="spin"></span>Loading from NEAR…</p>`;
  try {
    if (h.startsWith("#/model/")) await pageModel(Number(h.split("/")[2]));
    else if (h === "#/contribute") pageContribute();
    else if (h === "#/earnings") await pageEarnings();
    else if (h === "#/create") pageCreate();
    else await pageModels();
  } catch (e) {
    view.innerHTML = `<div class="notice warn">${esc(e.message)}</div>`;
  }
}

(async () => {
  CONFIG = await api("/api/config");
  $("#net").textContent = `NEAR ${CONFIG.network}`;
  $("#contract-link").innerHTML = `Contract ${acctLink(CONFIG.contract)}`;
  window.addEventListener("hashchange", route);
  route();
})();

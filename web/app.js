// Axon web app - plain JS, no build step. Reads the NEAR contract through the app backend.
const $ = (s, r = document) => r.querySelector(s);
const view = $("#view");
const COLORS = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)", "var(--s5)"];
const YOCTO = 1e24;
let CONFIG = null;
let RUNS = null;
let ART = null;

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const near = (y, d = 4) => (Number(y) / YOCTO).toFixed(d);
const short = (a) => (a.split(".").length > 2 ? a.split(".")[0] : a);
const pct = (s, t) => ((100 * Number(s)) / (Number(t) || 1)).toFixed(1) + "%";
const txLink = (h) => (h ? `<a class="mono" target="_blank" rel="noopener" href="${CONFIG.explorer}/txns/${h}">${h.slice(0, 8)}…</a>` : "");
const acctLink = (a) => `<a target="_blank" rel="noopener" title="${esc(a)}" href="${CONFIG.explorer}/address/${a}">${esc(short(a))}</a>`;
const flat = (t) => String(t || "").split(/\s+/).join(" ");

// ------------------------------------------------------------------ data
// The app backend when one is reachable (it also reaches the vault, so questions can be asked). Without one
// (static hosting) the page reads the NEAR contract straight from an RPC node and shows the published runs.
let API = "";
let LIVE = false;

async function api(path, opts = {}) {
  const r = await fetch(API + path, { headers: { "content-type": "application/json" }, ...opts });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body.detail || r.statusText);
  return body;
}

async function rpcView(method, args = {}) {
  const b64 = btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(args))));
  const r = await fetch(CONFIG.rpc, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: "axon", method: "query", params: { request_type: "call_function", finality: "final", account_id: CONFIG.contract, method_name: method, args_base64: b64 } }),
  }).then((x) => x.json());
  if (r.error || r.result?.error) throw new Error("NEAR RPC: " + JSON.stringify(r.error || r.result.error).slice(0, 160));
  return JSON.parse(new TextDecoder().decode(new Uint8Array(r.result.result)));
}

const db = {
  models: () => (LIVE ? api("/api/models") : rpcView("get_models", { limit: 50 })),
  async model(id) {
    if (LIVE) return api(`/api/models/${id}`);
    const m = await rpcView("get_model", { model_id: id });
    if (!m) throw new Error("no such model");
    m.rounds_detail = await rpcView("get_rounds", { model_id: id });
    return m;
  },
  async runs() {
    if (LIVE) return api("/api/runs");
    const all = await fetch("/static/runs.json").then((r) => (r.ok ? r.json() : [])).catch(() => []);
    return all.filter((r) => r.contract === CONFIG.contract);
  },
  async earnings(account) {
    if (LIVE) return api(`/api/earnings/${encodeURIComponent(account)}`);
    const out = [];
    for (const m of await rpcView("get_models", { limit: 50 })) {
      const c = m.contributors.find((c) => c.account === account);
      if (c || m.creator === account) {
        out.push({ model_id: m.id, name: m.name, shares: c ? c.shares : "0", total_shares: m.total_shares, earnings: await rpcView("earnings_of", { model_id: m.id, account }) });
      }
    }
    return out;
  },
};

async function boot() {
  const site = await fetch("/static/site.json").then((r) => (r.ok ? r.json() : {})).catch(() => ({}));
  API = site.api || "";
  try {
    CONFIG = await api("/api/config", { signal: AbortSignal.timeout(20000) });
    LIVE = true;
  } catch {
    LIVE = false;
    CONFIG = { network: site.network || "mainnet", contract: site.contract, tokens: [], vault: null, demo_payer: null };
  }
  CONFIG.rpc = CONFIG.rpc || site.rpc || (CONFIG.network === "mainnet" ? "https://free.rpc.fastnear.com" : "https://rpc.testnet.fastnear.com");
  CONFIG.explorer = CONFIG.explorer || (CONFIG.network === "mainnet" ? "https://nearblocks.io" : "https://testnet.nearblocks.io");
  CONFIG.video = site.video || null;
}

// Example models show the range of the platform. Clearly marked: they are not live.
const EXAMPLES = [
  { name: "Scam Detector", domain: "security", text: "Wallet users pool the scam messages they received, so the model spots new scam scripts first." },
  { name: "Drug Safety", domain: "pharma", text: "Labs pool private compound test results to predict toxicity earlier." },
  { name: "Contract Helper", domain: "legal", text: "Law firms pool private contracts to train a drafting assistant they co-own." },
];

function owners(m) {
  return m.contributors.slice().sort((a, b) => Number(b.shares) - Number(a.shares));
}

// Each contributor trains on their own machine, so the neuron shows their device, not their name.
const DEVICES = [
  // laptop
  `<svg viewBox="0 0 40 30" aria-hidden="true"><rect x="7" y="3" width="26" height="17" rx="1.5"/><rect x="10" y="6" width="20" height="11"/><path d="M3 23h34l-3 4H6z"/><path d="M17 25h6"/></svg>`,
  // desktop tower with a GPU
  `<svg viewBox="0 0 40 30" aria-hidden="true"><rect x="12" y="2" width="16" height="26" rx="1.5"/><path d="M15 6h10M15 9h10"/><rect x="15" y="15" width="10" height="5"/><circle cx="18" cy="17.5" r="1.2"/><circle cx="22" cy="17.5" r="1.2"/><circle cx="20" cy="24" r="1.3"/></svg>`,
  // mini server
  `<svg viewBox="0 0 40 30" aria-hidden="true"><rect x="6" y="4" width="28" height="7" rx="1"/><rect x="6" y="12" width="28" height="7" rx="1"/><rect x="6" y="20" width="28" height="7" rx="1"/><circle cx="10" cy="7.5" r="1"/><circle cx="10" cy="15.5" r="1"/><circle cx="10" cy="23.5" r="1"/><path d="M22 7.5h8M22 15.5h8M22 23.5h8"/></svg>`,
  // GPU card
  `<svg viewBox="0 0 40 30" aria-hidden="true"><rect x="3" y="7" width="31" height="15" rx="1.5"/><circle cx="13" cy="14.5" r="5"/><circle cx="25" cy="14.5" r="5"/><path d="M13 11v7M9.5 14.5h7M25 11v7M21.5 14.5h7"/><path d="M34 10h3v9h-3M7 22v3M12 22v3M17 22v3M22 22v3"/></svg>`,
];

function neuronContributors(m) {
  if (!m) return [0, 1, 2].map((i) => ({ html: DEVICES[i], title: "contributor" }));
  const o = owners(m);
  const good = o.filter((c) => Number(c.shares) > 0);
  const bad = o.filter((c) => Number(c.shares) === 0 && m.rounds > 0);
  const dev = (c, i) => ({ html: DEVICES[i % DEVICES.length], title: `${short(c.account)} · ${pct(c.shares, m.total_shares)}` });
  const list = good.map((c, i) => dev(c, i));
  // Excluded contributors: same device, greyed out and crossed, placed mid-fan so it reads clearly.
  bad.forEach((c, k) => list.splice(Math.ceil(list.length / 2), 0, { ...dev(c, good.length + k), excluded: true, title: `${short(c.account)} · 0%, excluded` }));
  return list;
}

function featured(models) {
  return models.slice().sort((a, b) => b.rounds - a.rounds || b.queries - a.queries || b.id - a.id)[0] || null;
}

async function runs() {
  if (!RUNS) RUNS = await db.runs().catch(() => []);
  return RUNS;
}

// ------------------------------------------------------------------ home

async function pageHome() {
  const models = await db.models();
  const f = featured(models);
  const totals = models.reduce((t, m) => ({ q: t.q + m.queries, r: t.r + Number(m.total_revenue), o: t.o + m.contributors.filter((c) => Number(c.shares) > 0).length }), { q: 0, r: 0, o: 0 });
  view.innerHTML = `
    <section class="hero">
      <canvas class="art" id="art" aria-label="A neuron: contributors' signals flow into one model"></canvas>
      <div class="labels" id="labels"></div>
      <div class="copy">
        <div class="eyebrow">Private AI, co-owned on NEAR</div>
        <h1>Your private data trains models in a specific niche. <span class="dim">Contributors own the model and get paid on what it earns.</span></h1>
        <p class="sub">Your data never leaves your machine. A sealed vault scores how much it helped, and a NEAR contract records who owns what and pays them.</p>
        <div class="cta"><a class="btn" href="#/models">Browse models</a><a class="btn ghost" href="#/contribute">Contribute data</a></div>
        <p class="newhere">New here? <a href="#/how">How it works</a>, in five steps.</p>
      </div>
      <div class="term" id="term"></div>
      <div class="ticker"><div class="track" id="ticker"></div></div>
    </section>
    <div class="wrap">
      <section class="block" id="models">
        <div class="kicker">Models</div>
        <h2>One model per niche. Owned by the people who trained it.</h2>
        <p class="lead">Each model starts from a free open base model and is fine-tuned on its contributors' private data. Anyone can start a model for any topic, and anyone can join later.</p>
        <div class="grid">${models.map(modelCard).join("") || `<p class="muted">No models yet. <a href="#/create">Start one</a>.</p>`}
          ${EXAMPLES.map((e) => `<div class="card example"><span class="tag">${esc(e.domain)} · example</span><h3>${esc(e.name)}</h3><p class="muted small">${esc(e.text)}</p></div>`).join("")}</div>
      </section>
      <section class="block" id="compare">${await nicheBlock(models, f)}</section>
      <section class="block" id="how">${howBlock()}</section>
      <section class="block">${trustBlock()}</section>
    </div>`;
  ART = AxonNeuron.mount($("#art"), {
    contributors: neuronContributors(f), labels: $("#labels"),
    axonLabel: "<b>inference</b>",
  });
  ticker(models, totals);
  typeTerm(f);
  if (location.hash.startsWith("#/how") || location.hash === "#/models") {
    const id = location.hash === "#/models" ? "models" : "how";
    requestAnimationFrame(() => document.getElementById(id).scrollIntoView({ behavior: "smooth" }));
  }
}

function ticker(models, t) {
  const v = LIVE ? CONFIG.vault?.attestation?.mode || "unknown" : "offline · answers recorded";
  const items = [
    `Network <b>NEAR ${esc(CONFIG.network)}</b>`, `Contract <b>${esc(CONFIG.contract)}</b>`, `Models <b>${models.length}</b>`,
    `Owners <b>${t.o}</b>`, `Paid questions <b>${t.q}</b>`, `Paid to owners <b>${near(t.r, 3)} Ⓝ</b>`,
    `Split <b>95% owners · 5% Axon</b>`, `Vault <b>${esc(v)}</b>`, `Data <b>never leaves the device</b>`,
    `Junk data <b>earns 0%</b>`, `Base models <b>open: Qwen · Llama · Gemma · Mistral</b>`,
  ];
  const html = items.map((i) => `<span>${i}</span>`).join("");
  $("#ticker").innerHTML = html + html;
}

function typeTerm(f) {
  const el = $("#term");
  if (!el) return;
  const id = f ? f.id : 0, price = f ? Number(f.query_price) : 1e22;
  const o = f ? owners(f).filter((c) => Number(c.shares) > 0).slice(0, 3).map((c) => `${short(c.account)} ${pct(c.shares, f.total_shares)}`).join(" · ") : "owners by share";
  const lines = [
    `<span class="p">&gt;</span> <b>axon.pay_for_query</b>({ model_id: ${id}, query_hash: "9c1e…4b07" })`,
    `<span class="p">&lt;</span> { to_owners: "${near(price * 0.95, 4)} Ⓝ", platform_fee: "${near(price * 0.05, 4)} Ⓝ" }`,
    `  // split by share: ${esc(o)}`,
  ];
  let i = 0, j = 0;
  const plain = lines.map((l) => l.replace(/<[^>]+>/g, "").replace(/&gt;/g, ">").replace(/&lt;/g, "<"));
  const tick = () => {
    if (!document.body.contains(el)) return;
    if (i >= lines.length) { el.innerHTML = lines.join("\n") + `\n<span class="cur"></span>`; setTimeout(() => { i = 0; j = 0; tick(); }, 6000); return; }
    j++;
    const done = lines.slice(0, i).join("\n");
    el.innerHTML = (done ? done + "\n" : "") + esc(plain[i].slice(0, j)) + `<span class="cur"></span>`;
    if (j >= plain[i].length) { i++; j = 0; }
    setTimeout(tick, j === 0 ? 450 : 22);
  };
  tick();
}

function modelCard(m) {
  const improved = m.base_eval_loss_milli && m.eval_loss_milli ? ((1 - m.eval_loss_milli / m.base_eval_loss_milli) * 100).toFixed(1) : null;
  const o = owners(m);
  return `<a class="card" href="#/model/${m.id}">
    <span class="tag live">${esc(m.domain)} · live</span>
    <h3>${esc(m.name)}</h3>
    <p class="muted small">${esc(m.description)}</p>
    <div class="minibar">${o.map((c, i) => `<span style="width:${pct(c.shares, m.total_shares)};background:${COLORS[i % 5]}"></span>`).join("")}</div>
    <div class="meta"><span>${o.filter((c) => Number(c.shares) > 0).length} owners</span><span>${m.rounds} rounds</span><span>${m.queries} paid questions</span>${improved ? `<span style="color:var(--accent)">${improved}% better</span>` : ""}</div>
  </a>`;
}

const COMPARE_HEAD = `<div class="kicker">Base model vs Axon-trained</div>
    <h2>Same question. One model learned from specialists.</h2>
    <p class="lead">Base models learned the public internet, so on specialist, private knowledge they guess. Each model below was fine-tuned by the people who hold that knowledge. The base model never saw their data; the Axon model was trained on it.</p>`;

// Home page: one tab per niche model that has a published run (the latest clean run of each).
async function nicheBlock(models, f) {
  const all = await runs();
  const shown = models.filter((m) => all.some((r) => r.model_id === m.id && !r.note && r.probes?.length))
    .sort((a, b) => b.id - a.id).filter((m, i, arr) => arr.findIndex((x) => x.domain === m.domain) === i);
  if (shown.length < 2) return compareBlock(shown[0] || f);
  setTimeout(() => {
    const pick = async (i) => {
      document.querySelectorAll("#nichetabs button").forEach((b, k) => b.classList.toggle("on", k === i));
      $("#niche").innerHTML = await compareBlock(shown[i], false);
    };
    document.querySelectorAll("#nichetabs button").forEach((b, i) => (b.onclick = () => pick(i)));
    pick(0);
  });
  return COMPARE_HEAD + `<div class="tabs" id="nichetabs" style="margin-bottom:26px">${shown.map((m) => `<button style="font-size:13px;padding:10px 16px">${esc(m.name)} <span class="muted">· ${esc(m.domain)}</span></button>`).join("")}</div><div id="niche"></div>`;
}

async function compareBlock(m, withHead = true) {
  const all = await runs();
  const run = m ? all.filter((r) => !r.note).find((r) => r.model_id === m.id) : all[0];
  const head = withHead ? COMPARE_HEAD : "";
  if (!run || !run.probes?.length) return head + `<div class="card muted">The comparison appears after this model's first published run.</div>`;
  // Group showcase questions by disease (a gene question and an inheritance question each).
  const groups = [];
  for (const p of run.probes) {
    const g = groups.find((x) => x.disease === (p.disease || p.question));
    g ? g.items.push(p) : groups.push({ disease: p.disease || p.question, contributor: p.contributor, items: [p] });
  }
  const base = esc(run.base_model.split("/").pop());
  setTimeout(() => {
    const box = $("#cmpbox");
    if (!box) return;
    const show = (k) => {
      document.querySelectorAll("#cmptabs button").forEach((b, i) => b.classList.toggle("on", i === k));
      const g = groups[k];
      const who = g.contributor ? short(g.contributor) : "the contributors";
      box.innerHTML = g.items.map((p) => `
        <div class="q">${esc(p.question)}</div>
        <div class="card"><h4>Base model · ${base}${marks(p, "base_model")}</h4><div class="answer">${esc(flat(p.base_model))}</div></div>
        <div class="card axon"><h4>Axon-trained${marks(p, "axon_trained")}</h4><div class="answer">${esc(flat(p.axon_trained))}</div></div>
        ${p.kind === "cwe" ? `<div class="why small muted">Right answer: <b style="color:var(--fg)">${esc(p.answer_label || p.answer)}</b></div>`
          : p.kind === "chrf" ? `<div class="why small muted">Human translation: <b style="color:var(--fg)">${esc(p.answer)}</b></div>`
          : p.kind ? `<div class="why small muted">Answer in ${esc(who)}'s data: <b style="color:var(--fg)">${esc(p.kind === "gene" ? p.gene + " gene" : p.inheritance)}</b>${p.reference ? `<div class="ref">${esc(flat(p.reference))}</div>` : ""}</div>` : ""}`).join("") + `
        <div class="card why"><h4>Why the Axon answer is better</h4>
          <p class="small" style="margin:0">${esc(g.items[0].why || `The base model saw little or nothing about ${g.disease} on the public internet, so it has to guess. The Axon model was trained on ${who}'s specialist data about it, so it answers from what the specialists know.`)}</p></div>`;
    };
    document.querySelectorAll("#cmptabs button").forEach((b, i) => (b.onclick = () => show(i)));
    show(0);
  });
  const L = run.hidden_test_loss;
  const rc = run.recall;
  const kpi = (v, l, hot) => `<div class="kpi"><div class="v"${hot ? ' style="color:var(--accent)"' : ""}>${v}</div><div class="l">${l}</div></div>`;
  const LABEL = { gene: "gene", inheritance: "inheritance", cwe: "weakness type", chrf: "translation score" };
  const kinds = rc ? Object.keys(LABEL).filter((k) => rc.base_model && rc.base_model[k + "_of"]) : [];
  const cell = (r, k) => (k === "chrf" ? `${r[k]}` : `${r[k]} / ${r[k + "_of"]}`);
  const score = kinds.length ? `<div class="kpis k4" style="margin:0 0 18px">${kinds.map((k) =>
      kpi(cell(rc.base_model, k), `${k === "chrf" ? "Translation score (chrF)" : "Right " + LABEL[k]} · base model`) +
      kpi(cell(rc.axon_trained, k), `${k === "chrf" ? "Translation score (chrF)" : "Right " + LABEL[k]} · Axon-trained`, true)).join("")}</div>` : "";
  return head + score + `
    <div class="tabs" id="cmptabs">${groups.map((g) => `<button>${esc(g.disease)}</button>`).join("")}</div>
    <div class="cmp" id="cmpbox"></div>
    <p class="small muted" style="margin-top:14px">Not cherry-picked: every showcase question of run <a href="https://github.com/haileymarshall/axon/blob/main/runs/${esc(run.run_id)}/summary.md">${esc(run.run_id)}</a> is shown and graded automatically (exact answer match, no human judging). On the vault's hidden test set (questions nobody trained on), loss went ${L.before.toFixed(3)} → ${L.after.toFixed(3)} (lower is better). Not medical advice.</p>`;
}

function marks(p, who) {
  const g = p.graded && p.graded[who];
  if (!g || !("correct" in g)) return "";
  if ("chrf" in g) return `<span style="margin-left:10px;color:${g.correct ? "var(--accent)" : "var(--warn)"}">chrF ${g.chrf}</span>`;
  return `<span style="margin-left:10px;color:${g.correct ? "var(--accent)" : "var(--warn)"}">${g.correct ? "✓ right" : "✗ wrong"}</span>`;
}

function howBlock() {
  return `<div class="kicker">How it works</div><h2>Five steps. Your data stays home.</h2>
    <p class="lead">Axon fine-tunes free open models (it does not train from scratch). Contributors own the part that makes the model an expert.</p>
    <div class="steps">
      <div class="step"><b>Join a model</b><p>Pick a niche model and register a device key on NEAR, so nobody can send updates in your name.</p></div>
      <div class="step"><b>Train locally</b><p>Your machine fine-tunes a small adapter on your private data. The data never leaves.</p></div>
      <div class="step"><b>Send a sealed update</b><p>Only the adapter goes out, encrypted to the vault (a TEE) and signed by your device.</p></div>
      <div class="step"><b>Get scored fairly</b><p>The vault measures how much your update improved the model on a hidden test (Shapley values). Junk earns 0%.</p></div>
      <div class="step"><b>Own and earn</b><p>Your score becomes your share on NEAR. Every paid question: 95% to owners by share, 5% to Axon.</p></div>
    </div>`;
}

function trustBlock() {
  const v = CONFIG.vault;
  return `<div class="kicker">Why you can trust the numbers</div><h2>Checked by code, not by us.</h2>
    <div class="grid" style="margin-top:28px">
      <div class="card"><span class="tag">Vault</span><h3>Runs in a TEE</h3><p class="muted small">The vault that merges and scores updates runs in Intel TDX. A hardware quote binds its key to its code hash. ${LIVE ? `Mode now: <b>${esc(v?.attestation?.mode || "unknown")}</b>.` : "Verified attestation: see <code>runs/tee/</code> in the repo."}</p></div>
      <div class="card"><span class="tag">Contract</span><h3>Only signed results count</h3><p class="muted small">The NEAR contract accepts a round only if the vault's registered key signed it, and rejects replays and unknown accounts.</p></div>
      <div class="card"><span class="tag">Payments</span><h3>Any token, split on-chain</h3><p class="muted small">Pay with NEAR or any token via NEAR Intents. The contract splits each payment: 95% to owners by share, 5% to Axon.</p></div>
    </div>`;
}

// ------------------------------------------------------------------ model page

async function pageModel(id) {
  const m = await db.model(id);
  const total = Number(m.total_shares) || 1;
  const o = owners(m);
  // Same formula as the contract's earnings_of: pending + shares * acc_per_share / 1e9 - reward_debt
  const acc = BigInt(m.acc_per_share);
  const earnings = o.map((c) => (BigInt(c.pending) + (BigInt(c.shares) * acc) / 1000000000n - BigInt(c.reward_debt)).toString());
  const vault = CONFIG.vault;
  const keyOk = vault && vault.combiner_key === m.combiner_key && vault.code_hash === m.combiner_code_hash;
  const demo = !!CONFIG.demo_payer;

  view.innerHTML = `
    <section class="mhead">
      <canvas class="art" id="art"></canvas><div class="labels" id="labels"></div>
      <div class="copy"><a href="#/models" class="small muted">← All models</a>
        <div class="eyebrow" style="margin:14px 0 0">${esc(m.domain)} · model ${m.id}</div>
        <h1>${esc(m.name)}</h1><p class="muted">${esc(m.description)}</p>
        ${m.status !== "Closed" ? `<div class="row"><a class="btn" href="#/model/${m.id}/join">Join this model</a><a class="btn ghost" href="#ask" onclick="event.preventDefault();document.getElementById('q')?.focus()">Ask it</a></div>` : ""}</div>
    </section>
    <div class="wrap">
    <div class="kpis">
      <div class="kpi"><div class="v">${o.filter((c) => Number(c.shares) > 0).length}</div><div class="l">Owners</div></div>
      <div class="kpi"><div class="v">${m.rounds}</div><div class="l">Training rounds</div></div>
      <div class="kpi"><div class="v">${m.base_eval_loss_milli ? (m.base_eval_loss_milli / 1000).toFixed(2) + " → " + (m.eval_loss_milli / 1000).toFixed(2) : "–"}</div><div class="l">Hidden-test loss</div></div>
      <div class="kpi"><div class="v">${m.queries}</div><div class="l">Paid questions</div></div>
      <div class="kpi"><div class="v">${near(m.total_revenue, 3)} Ⓝ</div><div class="l">Paid to owners</div></div>
    </div>
    <div class="two">
      <div class="card">
        <h3>Who owns this model</h3>
        <p class="muted small">Share = how much each contributor's private data improved the model on a hidden test. Data that doesn't help earns nothing.</p>
        <div class="bar">${o.map((c, i) => `<span style="width:${(100 * Number(c.shares)) / total}%;background:${COLORS[i % 5]}" title="${esc(c.account)}"></span>`).join("")}</div>
        <table>
          <tr><th>Owner</th><th class="num">Share</th><th class="num">Rounds</th><th class="num">Earned</th></tr>
          ${o.map((c, i) => `<tr>
            <td><span class="dot" style="background:${COLORS[i % 5]}"></span>${acctLink(c.account)}${Number(c.shares) === 0 && m.rounds ? ` <span class="small zero">excluded: made the model worse</span>` : ""}</td>
            <td class="num ${Number(c.shares) === 0 ? "zero" : ""}">${((100 * Number(c.shares)) / total).toFixed(1)}%</td>
            <td class="num">${c.rounds}</td>
            <td class="num">${near(earnings[i], 5)} Ⓝ</td></tr>`).join("")}
        </table>
      </div>
      <div class="card">${LIVE ? askCard(m, demo) : offlineCard()}</div>
    </div>
    <section class="block" id="compare">${await compareBlock(m)}</section>
    <section class="block">
      <div class="kicker">Training</div><h2>Every round, on-chain.</h2>
      <div class="two" style="margin-top:28px">
        <div class="card chart">${lossChart(m)}</div>
        <div class="card"><table><tr><th>Round</th><th class="num">Test loss</th><th class="num">Shares minted</th><th>Excluded</th><th class="num">Tx</th></tr>
          ${m.rounds_detail.slice().reverse().map((r) => `<tr><td>#${r.round}</td><td class="num">${(r.eval_loss_milli / 1000).toFixed(3)}</td>
            <td class="num">${r.results.reduce((s, x) => s + Number(x.shares), 0).toLocaleString()}</td>
            <td class="small">${r.results.filter((x) => Number(x.shares) === 0).map((x) => esc(short(x.account))).join(", ") || "–"}</td>
            <td class="num small">${r.adapter_hash ? r.adapter_hash.slice(0, 8) + "…" : ""}</td></tr>`).join("") || `<tr><td colspan="5" class="muted">No rounds yet.</td></tr>`}
        </table></div>
      </div>
    </section>
    <section class="block">
      <div class="kicker">Proof</div><h2>Why you can trust these numbers</h2>
      <div class="card small" style="margin-top:28px">
        <p>Round results are signed by the vault key <code>${esc(m.combiner_key.slice(0, 16))}…</code>, bound to vault code hash <code>${esc(m.combiner_code_hash.slice(0, 16))}…</code>. The contract rejects anything else.</p>
        <p>${!LIVE ? "The vault is offline right now; the model stays bound on-chain to the key and code hash above." : keyOk ? "✅ The running vault's key and code hash match what is registered on-chain." : "⚠️ The vault currently online is not the one this model is bound to (answers need the vault that trained it)."}
        ${LIVE ? `Attestation mode: <b>${esc(vault?.attestation?.mode || "unknown")}</b>.` : ""}</p>
        <p style="margin-bottom:0">Base model <code>${esc(m.base_model)}</code> (open, free). Compute providers get a fixed fee per round (${near(m.compute_fee, 3)} Ⓝ), never ownership. Training budget left: ${near(m.budget, 3)} Ⓝ. Creator ${acctLink(m.creator)}.</p>
      </div>
    </section>
    </div>`;

  ART = AxonNeuron.mount($("#art"), {
    contributors: neuronContributors(m), labels: $("#labels"), center: [0.66, 0.52], scale: 17, cell: 4, seed: 11 + m.id,
  });
  if (LIVE) {
    $("#asset").onchange = (e) => ($("#refund-wrap").style.display = ["demo", "wallet"].includes(e.target.value) ? "none" : "block");
    $("#askbtn").onclick = () => ask(m);
  }
}

function askCard(m, demo) {
  return `<h3>Ask this model</h3>
    <p class="muted small">Your question goes only to the sealed vault. Each paid question is split on-chain: 95% to the owners, 5% to Axon.</p>
    <textarea id="q" placeholder="e.g. Which gene is involved in Laing distal myopathy, and how is it inherited?"></textarea>
    <label>Pay with</label>
    <select id="asset">
      <option value="wallet">My NEAR wallet${W.account() ? " · " + esc(W.account()) : " (connect)"}</option>
      ${demo ? `<option value="demo">Free demo question (Axon pays, ${CONFIG.demo_per_day} a day)</option>` : ""}
      ${CONFIG.tokens.map((t) => `<option value="${t.id}">${esc(t.label)} · via NEAR Intents</option>`).join("")}
    </select>
    <div id="refund-wrap" style="display:none"><label>Your refund address on that chain</label><input id="refund" placeholder="0x… / So1… / bc1…"></div>
    <label class="check"><input type="checkbox" id="compare" checked> Compare with the original open model (${esc(m.base_model.split("/").pop())}, free)</label>
    <div class="row"><button class="btn" id="askbtn">Pay ${near(m.query_price, 3)} Ⓝ and ask</button></div>
    <div id="askout"></div>`;
}

function offlineCard() {
  return `<h3>Ask this model</h3>
    <p class="muted small">The vault that holds this model runs on a rented GPU, so it is only switched on at certain times. It is offline right now.</p>
    <div class="notice">Everything on this page is read live from the NEAR contract. The model's real answers, next to the base model's, are below${CONFIG.video ? `, and in the <a href="${esc(CONFIG.video)}" target="_blank" rel="noopener">demo video</a>` : ""}.</div>
    <div class="row"><a class="btn ghost" href="#compare" onclick="event.preventDefault();document.getElementById('compare').scrollIntoView({behavior:'smooth'})">See recorded answers</a></div>`;
}

function lossChart(m) {
  const pts = [{ round: 0, loss: m.rounds_detail.length ? m.base_eval_loss_milli / 1000 : null }, ...m.rounds_detail.map((r) => ({ round: r.round, loss: r.eval_loss_milli / 1000 }))].filter((p) => p.loss != null);
  if (pts.length < 2) return `<p class="muted small">The loss curve appears after the first round.</p>`;
  const W = 400, H = 190, P = 34;
  const ls = pts.map((p) => p.loss), lo = Math.min(...ls), hi = Math.max(...ls), span = hi - lo || 1;
  const x = (i) => P + (i * (W - 2 * P)) / (pts.length - 1);
  const y = (l) => 30 + ((hi - l) / span) * (H - 64);
  const path = pts.map((p, i) => `${i ? "L" : "M"}${x(i)},${y(p.loss)}`).join(" ");
  return `<h3>Hidden-test loss <span class="muted small">(lower is better)</span></h3><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Loss per round">
    <path d="${path}" fill="none" stroke="var(--accent)" stroke-width="2"/>
    ${pts.map((p, i) => `<rect x="${x(i) - 4}" y="${y(p.loss) - 4}" width="8" height="8" fill="var(--accent)"/><text x="${x(i)}" y="${H - 8}" text-anchor="middle">${i === 0 ? "base" : "round " + p.round}</text><text x="${x(i)}" y="${y(p.loss) - 12}" text-anchor="middle">${p.loss.toFixed(3)}</text>`).join("")}
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
    if (asset === "wallet") {
      if (!W.account()) { W.connect(); throw new Error("Connect your wallet first (top right), then click again."); }
      out.innerHTML = `<p class="small"><span class="spin"></span>Confirm the payment in your wallet…</p>`;
      const compare = $("#compare").checked;
      W.pending.set({ kind: "ask", model_id: m.id, question: q, compare });  // in case the wallet redirects
      const tx = await W.call("pay_for_query", { model_id: m.id, source: "wallet", query_hash: await sha256hex(q) }, m.query_price, 30);
      W.pending.take();
      await answerPaid(m.id, q, tx, W.account(), compare, out);
    } else if (asset === "demo") {
      out.innerHTML = `<p class="small"><span class="spin"></span>Paying on-chain, then asking the vault…</p>`;
      const r = await api("/api/ask-demo", { method: "POST", body: JSON.stringify({ model_id: m.id, question: q, compare: $("#compare").checked }) });
      out.innerHTML = answerHtml(r) + `<p class="small muted">Paid by ${acctLink(r.payer)} · tx ${txLink(r.payment_tx)} · 95% to the owners, 5% to Axon · not medical advice</p>`;
    } else {
      const refund = $("#refund").value.trim();
      if (!refund) throw new Error("Enter a refund address on the chain you're paying from.");
      out.innerHTML = `<p class="small"><span class="spin"></span>Getting a NEAR Intents quote…</p>`;
      const r = await api("/api/quote", { method: "POST", body: JSON.stringify({ model_id: m.id, origin_asset: asset, refund_to: refund, question: q, dry: false, compare: $("#compare").checked }) });
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

async function sha256hex(text) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function answerPaid(modelId, question, tx, payer, compare, out) {
  out.innerHTML = `<p class="small"><span class="spin"></span>Paid (tx ${txLink(tx)}). Asking the vault…</p>`;
  const r = await api("/api/ask-paid", { method: "POST", body: JSON.stringify({ model_id: modelId, question, payment_tx: tx, payer, compare }) });
  out.innerHTML = answerHtml(r) + `<p class="small muted">Paid from your wallet ${acctLink(payer)} · tx ${txLink(tx)} · 95% to the owners, 5% to Axon</p>`;
}

// Wallets that redirect (e.g. MyNEARWallet) come back with ?transactionHashes=...: finish what was started.
async function resumeAfterWallet() {
  const qs = new URLSearchParams(location.search);
  const tx = (qs.get("transactionHashes") || "").split(",")[0];
  if (!tx && !qs.get("errorCode")) return;
  history.replaceState(null, "", location.pathname + location.hash);
  const p = W.pending.take();
  if (!p || !tx) return;
  if (p.kind === "ask") {
    location.hash = `#/model/${p.model_id}`;
    await route();
    const out = $("#askout");
    if (out && $("#q")) { $("#q").value = p.question; await answerPaid(p.model_id, p.question, tx, W.account(), p.compare, out).catch((e) => (out.innerHTML = `<div class="notice warn">${esc(e.message)}</div>`)); }
  } else if (p.kind === "create") {
    await finishCreate(p, tx);
  } else if (p.kind === "withdraw") {
    location.hash = "#/earnings";
  }
}

// The Axon-trained answer, and (when asked) the original open model's answer to the same question, side by side.
function answerHtml(r) {
  if (!r.base_answer) return `<div class="answer box">${esc(r.answer)}</div>`;
  return `<div class="cmp" style="margin-top:14px">
    <div class="card"><h4>Original · ${esc((r.base_model || "").split("/").pop())} · free</h4><div class="answer">${esc(r.base_answer)}</div></div>
    <div class="card axon"><h4>Axon-trained · paid to its owners</h4><div class="answer">${esc(r.answer)}</div></div></div>`;
}

async function pollOrder(dep, modelId) {
  try {
    const o = await api(`/api/orders/${dep}`);
    if (o.state === "answered") {
      $("#askout").innerHTML = answerHtml(o) + `<p class="small muted">Paid via NEAR Intents (${esc(o.source)}) · tx ${txLink(o.payment_tx)}</p>`;
      return;
    }
    const s = $("#ostate");
    if (s) s.innerHTML = `<span class="spin"></span>Intents status: ${esc(o.intents_status || "waiting")}`;
  } catch (e) { /* keep polling */ }
  if (location.hash === `#/model/${modelId}`) setTimeout(() => pollOrder(dep, modelId), 5000);
}

// ------------------------------------------------------------------ other pages

// Three ways to do things: on the website, with your AI assistant, or as a developer.
function threeTabs(id, tabs) {
  setTimeout(() => {
    const show = (k) => {
      document.querySelectorAll(`#${id} > .tabs button`).forEach((b, i) => b.classList.toggle("on", i === k));
      document.querySelectorAll(`#${id} > .tabpane`).forEach((d, i) => (d.style.display = i === k ? "block" : "none"));
    };
    document.querySelectorAll(`#${id} > .tabs button`).forEach((b, i) => (b.onclick = () => show(i)));
    show(0);
  });
  return `<div id="${id}"><div class="tabs" style="margin-bottom:18px">${tabs.map((t) => `<button style="font-size:13px;padding:10px 16px">${t.title}</button>`).join("")}</div>
    ${tabs.map((t) => `<div class="tabpane">${t.html}</div>`).join("")}</div>`;
}

function copyBox(text, label = "Copy") {
  const id = "c" + Math.random().toString(36).slice(2, 8);
  setTimeout(() => { const b = document.getElementById(id); if (b) b.onclick = async () => { try { await navigator.clipboard.writeText(text); b.textContent = "Copied ✓"; } catch { b.textContent = "Select and copy"; } }; });
  return `<pre style="white-space:pre-wrap">${esc(text)}</pre><div class="row"><button class="btn" id="${id}">${label}</button></div>`;
}

const REPO = "https://github.com/haileymarshall/axon";
const envLine = () => `export AXON_NETWORK=${CONFIG.network} AXON_CONTRACT=${CONFIG.contract} AXON_VAULT_URL=${CONFIG.vault_url || "<vault address>"}`;

// What each demo niche wants from contributors, with one example line in the right format.
const NICHE = {
  "rare-diseases": { needs: "Questions and answers about rare genetic diseases you know first-hand (patients, families, clinics).",
    example: { q: "How is Rothmund-Thomson syndrome passed down in families?", a: "This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations." } },
  security: { needs: "Vulnerability reports you found or triaged, each labelled with its weakness type (CWE).",
    example: { q: "Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.\n\nVulnerability: A stored XSS in the comment form lets attackers inject script.", a: "CWE-79: Cross-site Scripting (XSS)." } },
  basque: { needs: "English sentences and your own Basque translation of each.",
    example: { q: "Translate into Basque: The train arrived on time.", a: "Trena garaiz iritsi zen." } },
};
const nicheOf = (m) => NICHE[m.domain] || { needs: m.description || "Questions and the answers you know are right, about this model's niche.", example: { q: "…", a: "…" } };

async function pageContribute() {
  const models = await db.models();
  const open = models.filter((m) => m.status !== "Closed");
  view.innerHTML = `<div class="wrap page">
    <div class="kicker">Contribute</div><h2>Contribute your data. Keep it.</h2>
    <p class="lead">Pick a model in your niche. The website prepares everything; the training runs on your own computer, so your data never leaves it. Only what the model learned is sent, sealed so only the vault can open it.</p>
    <div class="grid">${open.map((m) => `<div class="card"><span class="tag live">${esc(m.domain)}</span><h3>${esc(m.name)}</h3>
      <p class="muted small">${esc(nicheOf(m).needs)}</p><div class="row"><a class="btn" href="#/model/${m.id}/join">Join this model</a></div></div>`).join("") || `<p class="muted">No open models yet. <a href="#/create">Start one</a>.</p>`}</div>
    <section class="block">${howBlock()}</section></div>`;
}

async function pageJoin(id) {
  const m = await db.model(id);
  const n = nicheOf(m);
  const acct = W.account() || (CONFIG.network === "mainnet" ? "<your-account>.near" : "<your-account>.testnet");
  const cmd = `${envLine()}\n.venv/bin/python -m axon contribute --model ${m.id} --account ${acct} --data ~/my-axon-data.jsonl`;
  const prompt = `Help me contribute my private data to an Axon model, so I co-own it and earn from it. Follow the guide at ${REPO}/blob/main/AGENT_SETUP.md (Path A).
Model: ${m.id} ("${m.name}", niche: ${m.domain}) on NEAR ${CONFIG.network}, contract ${CONFIG.contract}.
My NEAR account: ${acct}.
Vault: ${CONFIG.vault_url || "see the Axon website"}.
My data is on this computer; it must never be uploaded or pasted anywhere. Help me turn it into the right format, then run the training.`;
  view.innerHTML = `<div class="wrap page">
    <a href="#/model/${m.id}" class="small muted">← ${esc(m.name)}</a>
    <div class="kicker" style="margin-top:18px">Join</div><h2>Join ${esc(m.name)}</h2>
    <p class="lead">Four steps. Your data stays on your computer the whole time.</p>
    <div class="steps s4">
      <div class="step"><b>Connect your wallet</b><p>${W.account() ? `Connected as <b>${esc(W.account())}</b>. Your earnings go here.` : `<a href="#" id="jconnect">Connect a NEAR wallet</a>. It's your account and where your earnings go.`}</p></div>
      <div class="step"><b>Get your data ready</b><p>${esc(n.needs)} One question and answer per line (below).</p></div>
      <div class="step"><b>Train on your computer</b><p>About 10 minutes on a GPU. Only the sealed "lesson learned" is sent, never your data.</p></div>
      <div class="step"><b>Own and earn</b><p>When the round closes, the vault scores everyone fairly. Your share shows here and on <a href="#/earnings">Earnings</a>.</p></div>
    </div>
    <section class="block" style="padding-top:50px">
      <h3>Your data file</h3><p class="muted small">A text file on your computer, e.g. <code>~/my-axon-data.jsonl</code>, one line per example, like this:</p>
      <pre style="white-space:pre-wrap">${esc(JSON.stringify(n.example))}</pre>
      <p class="muted small">Data that doesn't improve the model earns nothing, and is left out of it.</p>
    </section>
    <section class="block" style="padding-top:40px"><h3>Run the training</h3>
    ${threeTabs("jointabs", [
      { title: "With your AI assistant (easiest)", html: `<p class="muted small">Paste this into Claude, ChatGPT, Cursor or any assistant that can use a terminal. It installs Axon, helps you format your data, and runs the training for you.</p>${copyBox(prompt, "Copy message")}` },
      { title: "Copy one command", html: `<p class="muted small">Needs Axon installed (<a href="${REPO}/blob/main/AGENT_SETUP.md" target="_blank" rel="noopener">2-minute install</a>), your NEAR account imported, and an NVIDIA GPU (12 GB+).</p>${copyBox(cmd)}` },
      { title: "For developers", html: `<p class="muted small">Full details: install, keys, data format, troubleshooting.</p><pre>git clone ${REPO}.git && cd axon
python3 -m venv .venv && .venv/bin/pip install torch && .venv/bin/pip install -r requirements.txt
near account import-account using-seed-phrase network-config ${CONFIG.network}
${esc(cmd)}</pre><p class="small"><a href="${REPO}/blob/main/AGENT_SETUP.md" target="_blank" rel="noopener">AGENT_SETUP.md</a> · <a href="${REPO}" target="_blank" rel="noopener">README</a></p>` },
    ])}</section></div>`;
  const jc = $("#jconnect");
  if (jc) jc.onclick = (e) => { e.preventDefault(); W.connect(); };
}

async function pageEarnings() {
  const saved = W.account() || localStorageGet("axon.account") || "";
  view.innerHTML = `<div class="wrap page">
    <div class="kicker">Earnings</div><h2>Your earnings</h2><p class="lead">Your ownership in every model, and what it has earned you. Withdraw any time.</p>
    <div class="card"><label style="margin-top:0">NEAR account</label><div class="row" style="margin-top:0"><input id="acct" value="${esc(saved)}" placeholder="${CONFIG.network === "mainnet" ? "itziar.axon.ebukaa.near" : "alice.testnet"}" style="flex:1"><button class="btn" id="go">Show</button></div>
    ${W.account() ? "" : `<p class="small muted">Or <a href="#" id="econnect">connect your wallet</a> to see yours and withdraw with one click.</p>`}<div id="eout"></div></div></div>`;
  const ec = $("#econnect");
  if (ec) ec.onclick = (e) => { e.preventDefault(); W.connect(); };
  const run = async () => {
    const a = $("#acct").value.trim();
    if (!a) return;
    localStorageSet("axon.account", a);
    $("#eout").innerHTML = `<p class="small"><span class="spin"></span>Reading NEAR…</p>`;
    try {
      const rows = await db.earnings(a);
      const mine = W.account() && W.account() === a;
      $("#eout").innerHTML = rows.length ? `<table style="margin-top:16px"><tr><th>Model</th><th class="num">Ownership</th><th class="num">Withdrawable</th><th></th></tr>
        ${rows.map((r) => `<tr><td><a href="#/model/${r.model_id}">${esc(r.name)}</a></td><td class="num">${pct(r.shares, r.total_shares)}</td><td class="num">${near(r.earnings, 5)} Ⓝ</td>
          <td class="num">${mine && Number(r.earnings) > 0 ? `<button class="btn" data-w="${r.model_id}" style="padding:7px 12px">Withdraw</button>` : ""}</td></tr>`).join("")}</table>
        ${mine ? "" : `<p class="small muted">Connect this account's wallet to withdraw, or run <code>python -m axon withdraw --model &lt;id&gt; --account ${esc(a)}</code>.</p>`}` : `<p class="muted">This account doesn't own a share of any model yet.</p>`;
      document.querySelectorAll("[data-w]").forEach((b) => (b.onclick = async () => {
        b.disabled = true;
        try {
          W.pending.set({ kind: "withdraw" });
          const tx = await W.call("withdraw", { model_id: Number(b.dataset.w) }, "0", 30);
          W.pending.take();
          b.outerHTML = `<span class="small">sent · ${txLink(tx)}</span>`;
        } catch (e) { b.disabled = false; alert(e.message); }
      }));
    } catch (e) { $("#eout").innerHTML = `<div class="notice warn">${esc(e.message)}</div>`; }
  };
  $("#go").onclick = run;
  if (saved) run();
}

function pageCreate() {
  const v = CONFIG.vault;
  const bases = v?.bases || [{ id: "Qwen/Qwen3-1.7B", name: "Qwen3 1.7B", by: "Alibaba", note: "newest, 119 languages" }];
  const acct = W.account() || (CONFIG.network === "mainnet" ? "<your-account>.near" : "<your-account>.testnet");
  const prompt = `Help me start a new Axon model for my niche, following ${REPO}/blob/main/AGENT_SETUP.md (Path C).
Network: NEAR ${CONFIG.network}, contract ${CONFIG.contract}. My NEAR account: ${acct}. Vault: ${CONFIG.vault_url || "see the Axon website"}.
My niche: <describe it>. Help me write a small hidden test file (questions with the right answers) and create the model.`;
  const form = !LIVE || !v ? `<div class="notice">Creating a model binds it to the vault's key, so the vault has to be online. It is offline right now (it runs on a rented GPU at set times). You can still use the other two tabs to prepare.</div>` : `
    <div class="two">
      <div class="card">
        <label style="margin-top:0">Model name</label><input id="cname" placeholder="e.g. Sleep Coach" maxlength="64">
        <label>Niche (one or two words)</label><input id="cdomain" placeholder="e.g. sleep" maxlength="32">
        <label>What it does, and who trains it</label><textarea id="cdesc" maxlength="400" placeholder="e.g. Answers sleep questions. Trained by people on their own wearable data."></textarea>
        <label>Open base model</label><select id="cbase">${bases.map((b) => `<option value="${esc(b.id)}">${esc(b.name)} · ${esc(b.by)} · ${esc(b.note)}</option>`).join("")}</select>
        <div class="split" style="gap:12px"><div><label>Price per question (NEAR)</label><input id="cprice" value="0.01"></div><div><label>Training budget (NEAR)</label><input id="cbudget" value="0.06"></div></div>
        <label>Hidden test file (.jsonl, 5 to 500 lines)</label><input id="ctest" type="file" accept=".jsonl,.json,.txt">
        <p class="small muted">Questions with the right answers, one <code>{"q": "...", "a": "..."}</code> per line. It is sealed in your browser so only the vault can read it, and is how contributors get scored fairly.</p>
        <div class="row"><button class="btn" id="cgo">${W.account() ? "Create and sign" : "Connect wallet to create"}</button></div><div id="cout"></div>
      </div>
      <div class="card"><h3>What happens</h3><ol class="small muted" style="padding-left:18px;line-height:1.9">
        <li>Your wallet signs one transaction: the model is created on NEAR, bound to the vault, and the budget is deposited (it pays the GPU per round).</li>
        <li>Your test file is sealed to the vault. Nobody else, including us, can read it.</li>
        <li>The model appears on the home page with a <b>Join</b> button. Anyone with data in your niche can join.</li>
        <li>Every paid question: 95% to the contributors by share, 5% to Axon. Compute providers get a fixed fee, never ownership.</li></ol></div>
    </div>`;
  view.innerHTML = `<div class="wrap page">
    <div class="kicker">Create</div><h2>Start a model for any niche</h2>
    <p class="lead">Pick a free open model and one niche. People with private data in that niche train it with you, on their own computers, and own it together.</p>
    ${threeTabs("createtabs", [
      { title: "On the website", html: form },
      { title: "With your AI assistant", html: `<p class="muted small">Paste this into your assistant. It helps you write the test file and create the model.</p>${copyBox(prompt, "Copy message")}` },
      { title: "For developers", html: `<pre>${esc(envLine())}
.venv/bin/python -m axon create-model --creator ${esc(acct)} \\
  --name "Sleep Coach" --domain sleep \\
  --description "Trained on wearable sleep data from its owners" \\
  --price 0.01 --compute-fee 0.02 --budget 0.06</pre><p class="small muted">The model is bound on-chain to the vault's signing key and code hash. See <a href="${REPO}/blob/main/AGENT_SETUP.md" target="_blank" rel="noopener">AGENT_SETUP.md</a>.</p>` },
    ])}</div>`;
  const go = $("#cgo");
  if (go) go.onclick = () => createModel();
}

async function readTestFile() {
  const f = $("#ctest").files[0];
  if (!f) throw new Error("Choose your hidden test file.");
  const lines = (await f.text()).split(/\r?\n/).filter((l) => l.trim());
  const rows = lines.map((l, i) => { try { const r = JSON.parse(l); if (!r.q || !r.a) throw 0; return { q: String(r.q), a: String(r.a) }; } catch { throw new Error(`Line ${i + 1} of the test file is not {"q": ..., "a": ...}.`); } });
  if (rows.length < 5 || rows.length > 500) throw new Error("The test file needs 5 to 500 lines.");
  return rows.map((r) => JSON.stringify(r)).join("\n");
}

async function sealToVault(text) {
  const sodium = (await import("https://esm.sh/libsodium-wrappers@0.8.4")).default;
  await sodium.ready;
  const sealed = sodium.crypto_box_seal(new TextEncoder().encode(text), sodium.from_hex(CONFIG.vault.box_key));
  return sodium.to_base64(sealed, sodium.base64_variants.ORIGINAL);
}

const toYocto = (n) => { const [i, f = ""] = String(n).trim().split("."); return (BigInt(i || "0") * 10n ** 24n + BigInt((f + "0".repeat(24)).slice(0, 24))).toString(); };

async function createModel() {
  const out = $("#cout");
  try {
    if (!W.account()) { W.connect(); return; }
    const name = $("#cname").value.trim(), domain = $("#cdomain").value.trim().toLowerCase().replace(/[^a-z0-9-]+/g, "-");
    if (!name || !domain) throw new Error("Give the model a name and a niche.");
    const sealed = await sealToVault(await readTestFile());  // sealed before anything is signed
    const v = CONFIG.vault;
    const args = { name, domain, description: $("#cdesc").value.trim(), base_model: $("#cbase").value, combiner_key: v.combiner_key,
      combiner_code_hash: v.code_hash, query_price: toYocto($("#cprice").value), compute_fee: toYocto("0.02") };
    const p = { kind: "create", name, creator: W.account(), sealed };
    W.pending.set(p);
    out.innerHTML = `<p class="small"><span class="spin"></span>Confirm in your wallet…</p>`;
    const tx = await W.call("create_model", args, toYocto($("#cbudget").value), 50);
    W.pending.take();
    await finishCreate(p, tx);
  } catch (e) { out.innerHTML = `<div class="notice warn">${esc(e.message)}</div>`; }
}

async function finishCreate(p, tx) {
  location.hash = "#/create";
  const out = $("#cout") || view;
  out.innerHTML = `<p class="small"><span class="spin"></span>Created (tx ${txLink(tx)}). Sealing your test file to the vault…</p>`;
  for (let i = 0; i < 10; i++) {
    const m = (await db.models()).filter((x) => x.creator === p.creator && x.name === p.name).sort((a, b) => b.id - a.id)[0];
    if (m) {
      await api(`/api/models/${m.id}/test`, { method: "POST", body: JSON.stringify({ creator: p.creator, sealed: p.sealed }) });
      location.hash = `#/model/${m.id}`;
      return;
    }
    await new Promise((r) => setTimeout(r, 2000));
  }
  out.innerHTML = `<div class="notice warn">The model was created (tx ${txLink(tx)}) but did not show up yet. Refresh in a minute.</div>`;
}

function localStorageGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function localStorageSet(k, v) { try { localStorage.setItem(k, v); } catch { /* ignore */ } }

// ------------------------------------------------------------------ router

async function route() {
  const h = location.hash || "#/";
  document.querySelectorAll("nav a").forEach((a) => a.classList.toggle("on", a.getAttribute("href") === h));
  const onHome = ["#/", "#/how", "#/models", ""].includes(h);
  if (onHome && document.getElementById("art") && document.querySelector(".hero")) {
    const id = h === "#/how" ? "how" : h === "#/models" ? "models" : null;
    if (id) return document.getElementById(id).scrollIntoView({ behavior: "smooth" });
    return window.scrollTo({ top: 0, behavior: "smooth" });
  }
  window.scrollTo(0, 0);
  view.innerHTML = `<div class="wrap page"><p class="muted"><span class="spin"></span>Loading from NEAR…</p></div>`;
  try {
    if (/^#\/model\/\d+\/join/.test(h)) await pageJoin(Number(h.split("/")[2]));
    else if (h.startsWith("#/model/")) await pageModel(Number(h.split("/")[2]));
    else if (h === "#/contribute") await pageContribute();
    else if (h === "#/earnings") await pageEarnings();
    else if (h === "#/create") pageCreate();
    else await pageHome();
  } catch (e) {
    view.innerHTML = `<div class="wrap page"><div class="notice warn">${esc(e.message)}</div></div>`;
  }
}

// Wallet: a stub until wallet.js has loaded (it loads from a CDN), so pages never break without it.
const W = {
  account: () => (window.AxonWallet && window.AxonWallet.ready() ? window.AxonWallet.account() : null),
  connect: () => (window.AxonWallet && window.AxonWallet.ready() ? window.AxonWallet.connect() : alert("The wallet is still loading. Try again in a second.")),
  call: (...a) => window.AxonWallet.call(...a),
  pending: { set: (p) => window.AxonWallet && window.AxonWallet.pending.set(p), take: () => (window.AxonWallet ? window.AxonWallet.pending.take() : null) },
};

function walletButton() {
  const b = $("#wallet");
  if (!b) return;
  const a = W.account();
  b.textContent = a ? (a.length > 22 ? a.slice(0, 10) + "…" + a.slice(-8) : a) : "Connect wallet";
  b.title = a ? "Connected. Click to disconnect." : "Connect a NEAR wallet";
  b.onclick = () => (a ? (confirm(`Disconnect ${a}?`) && window.AxonWallet.disconnect()) : W.connect());
}

async function initWallet() {
  if (!window.AxonWallet) await new Promise((r) => window.addEventListener("axon-wallet-loaded", r, { once: true }));
  try {
    await window.AxonWallet.init(CONFIG.network, CONFIG.contract);
    window.AxonWallet.onChange(() => { walletButton(); if (["#/earnings", "#/create", "#/contribute"].includes(location.hash) || /\/join$/.test(location.hash)) route(); });
    walletButton();
    await resumeAfterWallet();
  } catch (e) {
    console.warn("wallet unavailable", e);
    const b = $("#wallet");
    if (b) b.style.display = "none";
  }
}

(async () => {
  await boot();
  $("#net").innerHTML = `<span class="live"></span>NEAR ${esc(CONFIG.network)}`;
  $("#contract-link").innerHTML = `Contract ${acctLink(CONFIG.contract)}`;
  window.addEventListener("hashchange", route);
  await route();
  initWallet();
})();

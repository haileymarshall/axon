// Axon hero art: a neuron, drawn at low resolution and rendered as dithered pixels.
// Dendrites = contributors (signals flow in), cell body = the model, axon = answers going out.
// A contributor whose data was excluded (0% share) gets a dim dendrite whose signals die before the cell body.
(function () {
  const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => (v + 0.5) / 16);

  function rng(seed) {
    let s = seed >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  }

  // A branch is a polyline in world units (soma radius = 1). Returns the branch and grows children.
  function grow(r, x, y, ang, len, w, depth, out, wiggle) {
    const pts = [[x, y]];
    let a = ang;
    const n = 9;
    for (let i = 1; i <= n; i++) {
      a += (r() - 0.5) * wiggle;
      x += (Math.cos(a) * len) / n;
      y += (Math.sin(a) * len) / n;
      pts.push([x, y]);
    }
    const b = { pts, w0: w, w1: w * 0.5, kids: [] };
    out.push(b);
    if (depth > 0) {
      const k = depth > 1 ? 2 : r() < 0.7 ? 2 : 1;
      for (let i = 0; i < k; i++) {
        const side = i === 0 ? -1 : 1;
        b.kids.push(grow(r, x, y, a + side * (0.3 + r() * 0.45), len * (0.55 + r() * 0.2), w * 0.55, depth - 1, out, wiggle));
      }
    }
    return b;
  }

  // Path from the tip of a dendrite (following first children) back to the soma, with cumulative lengths.
  function signalPath(b) {
    const chain = [];
    for (let c = b; c; c = c.kids[0]) chain.push(c);
    const pts = [];
    for (let i = chain.length - 1; i >= 0; i--) pts.push(...chain[i].pts.slice().reverse());
    const cum = [0];
    for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    return { pts, cum, len: cum[cum.length - 1] };
  }

  function at(path, s) {
    const d = s * path.len;
    let i = 1;
    while (i < path.cum.length - 1 && path.cum[i] < d) i++;
    const t = (d - path.cum[i - 1]) / (path.cum[i] - path.cum[i - 1] || 1);
    const a = path.pts[i - 1], b = path.pts[i];
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  }

  function build(contributors, seed) {
    const r = rng(seed);
    const dendrites = [];
    const n = Math.max(contributors.length, 3);
    // Contributor dendrites fan out over the left and top/bottom of the soma.
    for (let i = 0; i < n; i++) {
      const ang = Math.PI * (0.62 + (1.0 * (i + 0.5)) / n) + (r() - 0.5) * 0.12;
      const branches = [];
      const root = grow(r, Math.cos(ang) * 1.25, Math.sin(ang) * 1.25, ang, 2.0 + r() * 0.6, 0.78, 3, branches, 0.26);
      dendrites.push({ c: contributors[i] || null, branches, path: signalPath(root), tip: null, pulses: [] });
    }
    // Two small decorative dendrites on the right, so the cell looks like a cell.
    const extra = [];
    for (const ang of [-1.0, 1.15]) grow(r, Math.cos(ang) * 1.25, Math.sin(ang) * 1.25, ang, 1.1, 0.5, 2, extra, 0.35);
    // The axon: long, gently curving, with myelin beads and a terminal tuft.
    const axon = [];
    let x = 1.4, y = 0.25, a = 0.42;
    const pts = [[x, y]];
    for (let i = 0; i < 17; i++) {
      a += Math.sin(i * 0.35) * 0.025;
      x += Math.cos(a) * 0.2;
      y += Math.sin(a) * 0.2;
      pts.push([x, y]);
    }
    const terms = [];
    for (let i = 0; i < 4; i++) grow(r, x, y, a + (i - 1.5) * 0.5, 0.6 + r() * 0.3, 0.2, 1, terms, 0.5);
    const ap = { pts, cum: [0] };
    for (let i = 1; i < pts.length; i++) ap.cum.push(ap.cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    ap.len = ap.cum[ap.cum.length - 1];
    for (const d of dendrites) d.tip = d.path.pts[0];
    return { dendrites, extra, axon: ap, terms, axonEnd: [x, y] };
  }

  function mount(canvas, opts = {}) {
    const accent = opts.accent || [0, 236, 151];
    const cell = opts.cell || (window.innerWidth < 760 ? 3 : 5);
    const labels = opts.labels || null; // element to hold HTML labels
    let contributors = opts.contributors || [];
    let world = build(contributors, opts.seed || 7);
    const L = document.createElement("canvas"), A = document.createElement("canvas");
    const lx = L.getContext("2d", { willReadFrequently: true }), ax = A.getContext("2d", { willReadFrequently: true });
    const ctx = canvas.getContext("2d");
    let cols = 0, rows = 0, unit = 1, ox = 0, oy = 0, glow = 0, last = 0, visible = true, t0 = performance.now();
    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const center = opts.center || [0.31, 0.44];
    const scale = opts.scale || 16;

    function resize() {
      const w = canvas.clientWidth, h = canvas.clientHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cols = Math.ceil(w / cell);
      rows = Math.ceil(h / cell);
      L.width = A.width = cols;
      L.height = A.height = rows;
      const narrow = w < 760;
      unit = narrow ? Math.min(rows / (scale * 0.85), cols / (scale * 1.05)) : Math.min(rows / scale, cols / (scale * 1.6));
      ox = cols * (narrow ? 0.5 : center[0]);
      oy = rows * (narrow ? 0.42 : center[1]);
      placeLabels();
    }

    const P = (p, t) => [ox + (p[0] + Math.sin(t * 0.5 + p[1] * 1.7) * 0.03) * unit, oy + (p[1] + Math.cos(t * 0.4 + p[0] * 1.3) * 0.03) * unit];

    function strokeBranch(b, t, base, hi) {
      const n = b.pts.length;
      for (let i = 1; i < n; i++) {
        const w = (b.w0 + ((b.w1 - b.w0) * i) / n) * unit;
        const a = P(b.pts[i - 1], t), c = P(b.pts[i], t);
        lx.lineCap = "round";
        lx.strokeStyle = `rgb(${base},${base},${base})`;
        lx.lineWidth = Math.max(w, 0.8);
        lx.beginPath(); lx.moveTo(a[0], a[1]); lx.lineTo(c[0], c[1]); lx.stroke();
        if (w > 1.6) {
          lx.strokeStyle = `rgb(${hi},${hi},${hi})`;
          lx.lineWidth = w * 0.38;
          lx.beginPath(); lx.moveTo(a[0] - w * 0.18, a[1] - w * 0.22); lx.lineTo(c[0] - w * 0.18, c[1] - w * 0.22); lx.stroke();
        }
      }
    }

    function frame(now) {
      const t = (now - t0) / 1000;
      const dt = Math.min(0.05, (now - (last || now)) / 1000);
      last = now;
      lx.fillStyle = "#000"; lx.fillRect(0, 0, cols, rows);
      ax.clearRect(0, 0, cols, rows);

      // dendrites
      for (const d of world.dendrites) {
        const dead = d.c && d.c.excluded;
        for (const b of d.branches) strokeBranch(b, t, dead ? 48 : 150, dead ? 66 : 235);
      }
      for (const b of world.extra) strokeBranch(b, t, 105, 185);
      // axon + myelin beads + terminals
      const ap = world.axon;
      lx.lineCap = "round";
      for (let i = 1; i < ap.pts.length; i++) {
        const a = P(ap.pts[i - 1], t), c = P(ap.pts[i], t);
        lx.strokeStyle = "rgb(110,110,110)"; lx.lineWidth = Math.max(0.22 * unit, 1);
        lx.beginPath(); lx.moveTo(a[0], a[1]); lx.lineTo(c[0], c[1]); lx.stroke();
      }
      for (let i = 3; i + 3 < ap.pts.length; i += 5) {
        const a = P(ap.pts[i], t), c = P(ap.pts[i + 3], t);
        lx.strokeStyle = "rgb(170,170,170)"; lx.lineWidth = 0.55 * unit;
        lx.beginPath(); lx.moveTo(a[0], a[1]); lx.lineTo(c[0], c[1]); lx.stroke();
        lx.strokeStyle = "rgb(235,235,235)"; lx.lineWidth = 0.18 * unit;
        lx.beginPath(); lx.moveTo(a[0] - 0.1 * unit, a[1] - 0.14 * unit); lx.lineTo(c[0] - 0.1 * unit, c[1] - 0.14 * unit); lx.stroke();
      }
      for (const b of world.terms) {
        strokeBranch(b, t, 120, 190);
        const e = P(b.pts[b.pts.length - 1], t);
        lx.fillStyle = "rgb(200,200,200)"; lx.beginPath(); lx.arc(e[0], e[1], 0.22 * unit, 0, 7); lx.fill();
      }
      // soma: a lit sphere with a slightly irregular outline, and a nucleus
      const s = P([0, 0], t), R = unit * 1.55;
      const g = lx.createRadialGradient(s[0] - R * 0.38, s[1] - R * 0.42, R * 0.1, s[0], s[1], R * 1.08);
      g.addColorStop(0, "#fff"); g.addColorStop(0.55, "#a8a8a8"); g.addColorStop(1, "#1c1c1c");
      lx.fillStyle = g;
      lx.beginPath();
      for (let i = 0; i <= 40; i++) {
        const th = (i / 40) * Math.PI * 2, rr = R * (1 + 0.06 * Math.sin(th * 3 + 0.7) + 0.03 * Math.sin(th * 5 + t * 0.6));
        i ? lx.lineTo(s[0] + Math.cos(th) * rr, s[1] + Math.sin(th) * rr) : lx.moveTo(s[0] + Math.cos(th) * rr, s[1] + Math.sin(th) * rr);
      }
      lx.fill();
      const ng = lx.createRadialGradient(s[0] - R * 0.08, s[1] - R * 0.1, 0, s[0], s[1], R * 0.42);
      ng.addColorStop(0, "#5a5a5a"); ng.addColorStop(1, "#262626");
      lx.fillStyle = ng; lx.beginPath(); lx.arc(s[0] + R * 0.05, s[1] + R * 0.04, R * 0.38, 0, 7); lx.fill();

      // signals
      if (!reduce) {
        for (const d of world.dendrites) {
          const dead = d.c && d.c.excluded;
          if (Math.random() < dt * (dead ? 0.35 : 0.55)) d.pulses.push({ s: 0, v: 0.2 + Math.random() * 0.1 });
          for (const p of d.pulses) p.s += p.v * dt;
          for (const p of d.pulses) {
            const fade = dead ? Math.max(0, 1 - p.s / 0.45) : 1;
            if (fade <= 0) continue;
            const q = P(at(d.path, Math.min(p.s, 1)), t);
            const rg = ax.createRadialGradient(q[0], q[1], 0, q[0], q[1], unit * 0.34);
            const col = dead ? "150,150,150" : accent.join(",");
            rg.addColorStop(0, `rgba(${col},${0.95 * fade})`); rg.addColorStop(1, `rgba(${col},0)`);
            ax.fillStyle = rg; ax.beginPath(); ax.arc(q[0], q[1], unit * 0.34, 0, 7); ax.fill();
          }
          const arrived = d.pulses.filter((p) => p.s >= 1).length;
          if (!dead && arrived) glow = Math.min(1.6, glow + 0.5 * arrived);
          d.pulses = d.pulses.filter((p) => p.s < 1 && !(dead && p.s > 0.45));
        }
        if (glow > 0.9 && Math.random() < 0.35) { world.axon.pulses = world.axon.pulses || []; world.axon.pulses.push({ s: 0 }); glow -= 0.4; }
        for (const p of world.axon.pulses || []) {
          p.s += dt * 0.16;
          const q = P(at(world.axon, Math.min(p.s, 1)), t);
          const rg = ax.createRadialGradient(q[0], q[1], 0, q[0], q[1], unit * 0.3);
          rg.addColorStop(0, `rgba(${accent.join(",")},0.9)`); rg.addColorStop(1, `rgba(${accent.join(",")},0)`);
          ax.fillStyle = rg; ax.beginPath(); ax.arc(q[0], q[1], unit * 0.3, 0, 7); ax.fill();
        }
        if (world.axon.pulses) world.axon.pulses = world.axon.pulses.filter((p) => p.s < 1);
        glow = Math.max(0, glow - dt * 0.5);
      }
      const nucleus = 0.25 + Math.min(glow, 1) * 0.6 + 0.1 * Math.sin(t * 2);
      const cg = ax.createRadialGradient(s[0], s[1], 0, s[0], s[1], R * 0.4);
      cg.addColorStop(0, `rgba(${accent.join(",")},${nucleus})`); cg.addColorStop(1, `rgba(${accent.join(",")},0)`);
      ax.fillStyle = cg; ax.beginPath(); ax.arc(s[0], s[1], R * 0.4, 0, 7); ax.fill();

      // dither to the visible canvas
      const lum = lx.getImageData(0, 0, cols, rows).data, acc = ax.getImageData(0, 0, cols, rows).data;
      ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
      const levels = [[], [], [], []], hot = [];
      for (let j = 0; j < rows; j++) {
        for (let i = 0; i < cols; i++) {
          const k = (j * cols + i) * 4;
          const av = acc[k + 3] / 255;
          if (av > 0.22) { hot.push(i, j, av); continue; }
          const l = lum[k] / 255;
          if (l > 0.03 && l > BAYER[(j & 3) * 4 + (i & 3)] * 0.92) levels[Math.min(3, (l * 4) | 0)].push(i, j);
        }
      }
      const shades = ["rgba(240,238,232,0.32)", "rgba(240,238,232,0.55)", "rgba(244,242,236,0.8)", "rgba(250,249,245,1)"];
      for (let lv = 0; lv < 4; lv++) {
        ctx.fillStyle = shades[lv];
        const sz = cell * (0.5 + lv * 0.14), off = (cell - sz) / 2, arr = levels[lv];
        for (let m = 0; m < arr.length; m += 2) ctx.fillRect(arr[m] * cell + off, arr[m + 1] * cell + off, sz, sz);
      }
      ctx.fillStyle = `rgb(${accent.join(",")})`;
      for (let m = 0; m < hot.length; m += 3) {
        const sz = cell * (0.55 + 0.4 * Math.min(1, hot[m + 2])), off = (cell - sz) / 2;
        ctx.fillRect(hot[m] * cell + off, hot[m + 1] * cell + off, sz, sz);
      }
      if (visible && !reduce) requestAnimationFrame(frame);
    }

    function placeLabels() {
      if (!labels) return;
      labels.innerHTML = "";
      const add = (p, html, cls) => {
        const el = document.createElement("div");
        el.className = "nlabel " + (cls || "");
        el.innerHTML = html;
        labels.appendChild(el);
        const W = canvas.clientWidth, H = canvas.clientHeight, hw = el.offsetWidth / 2 + 6;
        el.style.left = `${Math.max(hw, Math.min(W - hw, ox * cell + p[0] * unit * cell))}px`;
        el.style.top = `${Math.max(el.offsetHeight * 1.4 + 4, Math.min(H - 8, oy * cell + p[1] * unit * cell))}px`;
        return el;
      };
      for (const d of world.dendrites) {
        if (!d.c) continue;
        const el = add(d.tip, d.c.html || `<b>${d.c.name}</b><span>${d.c.excluded ? "0% · excluded" : d.c.share}</span>`, (d.c.excluded ? "dead" : "") + (d.c.html ? " device" : ""));
        if (d.c.title) el.title = d.c.title;
      }
      if (opts.somaLabel) add([0, 2.0], opts.somaLabel, "soma");
      if (opts.axonLabel) add([world.axonEnd[0] + 0.2, world.axonEnd[1] + 1.25], opts.axonLabel, "axon");
    }

    window.addEventListener("resize", resize);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((es) => {
        const was = visible;
        visible = es[0].isIntersecting;
        if (visible && !was && !reduce) { last = 0; requestAnimationFrame(frame); }
      }).observe(canvas);
    }
    resize();
    requestAnimationFrame(frame);
    return {
      update(next) {
        contributors = next.contributors || contributors;
        Object.assign(opts, next);
        world = build(contributors, opts.seed || 7);
        placeLabels();
        if (reduce) requestAnimationFrame(frame);
      },
    };
  }

  window.AxonNeuron = { mount };
})();

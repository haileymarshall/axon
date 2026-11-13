// Axon design B art: an engraved, line-drawn neuron on a plain background.
// Dendrites = contributors (signals glide in), cell body = the model, axon = answers going out.
// A contributor whose data was excluded (0% share) gets a faded dendrite whose signals fizzle out.
// Same interface as design A's neuron.js: window.AxonNeuron.mount(canvas, opts).
(function () {
  function rng(seed) {
    let s = seed >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  }

  function grow(r, x, y, ang, len, w, depth, out, wiggle) {
    const pts = [[x, y]];
    let a = ang;
    const n = 10;
    for (let i = 1; i <= n; i++) {
      a += (r() - 0.5) * wiggle;
      x += (Math.cos(a) * len) / n;
      y += (Math.sin(a) * len) / n;
      pts.push([x, y]);
    }
    const b = { pts, w0: w, w1: w * 0.45, kids: [] };
    out.push(b);
    if (depth > 0) {
      const k = depth > 1 ? 2 : r() < 0.75 ? 2 : 1;
      for (let i = 0; i < k; i++) {
        b.kids.push(grow(r, x, y, a + (i === 0 ? -1 : 1) * (0.3 + r() * 0.45), len * (0.6 + r() * 0.15), w * 0.5, depth - 1, out, wiggle));
      }
    }
    return b;
  }

  function lengths(pts) {
    const cum = [0];
    for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    return { pts, cum, len: cum[cum.length - 1] };
  }

  function signalPath(b) {
    const chain = [];
    for (let c = b; c; c = c.kids[0]) chain.push(c);
    const pts = [];
    for (let i = chain.length - 1; i >= 0; i--) pts.push(...chain[i].pts.slice().reverse());
    return lengths(pts);
  }

  function at(path, s) {
    const d = Math.min(Math.max(s, 0), 1) * path.len;
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
    for (let i = 0; i < n; i++) {
      const ang = Math.PI * (0.6 + (1.05 * (i + 0.5)) / n) + (r() - 0.5) * 0.1;
      const branches = [];
      const root = grow(r, Math.cos(ang) * 1.15, Math.sin(ang) * 1.15, ang, 2.1 + r() * 0.5, 0.7, 3, branches, 0.24);
      dendrites.push({ c: contributors[i] || null, branches, path: signalPath(root), pulses: [] });
    }
    const extra = [];
    for (const ang of [-1.05, 1.2]) grow(r, Math.cos(ang) * 1.15, Math.sin(ang) * 1.15, ang, 1.2, 0.45, 2, extra, 0.3);
    let x = 1.3, y = 0.2, a = 0.38;
    const pts = [[x, y]];
    for (let i = 0; i < 22; i++) {
      a += Math.sin(i * 0.4) * 0.03;
      x += Math.cos(a) * 0.2;
      y += Math.sin(a) * 0.2;
      pts.push([x, y]);
    }
    const terms = [];
    for (let i = 0; i < 4; i++) grow(r, x, y, a + (i - 1.5) * 0.5, 0.65 + r() * 0.25, 0.18, 1, terms, 0.45);
    return { dendrites, extra, axon: Object.assign(lengths(pts), { pulses: [] }), terms, axonEnd: [x, y] };
  }

  function mount(canvas, opts = {}) {
    const ink = opts.ink || "242,244,255";
    const labels = opts.labels || null;
    let contributors = opts.contributors || [];
    let world = build(contributors, opts.seed || 7);
    const ctx = canvas.getContext("2d");
    let W = 0, H = 0, unit = 1, ox = 0, oy = 0, glow = 0, last = 0, visible = true;
    const t0 = performance.now();
    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function resize() {
      W = canvas.clientWidth;
      H = canvas.clientHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      unit = Math.min(H / 13.5, W / 15);
      ox = W * 0.47;
      oy = H * 0.5;
      placeLabels();
    }

    const P = (p, t) => [ox + (p[0] + Math.sin(t * 0.45 + p[1] * 1.6) * 0.025) * unit, oy + (p[1] + Math.cos(t * 0.38 + p[0] * 1.2) * 0.025) * unit];

    // A branch drawn as a bundle of fine parallel lines (engraving style).
    function hatch(b, t, alpha) {
      const pts = b.pts.map((p) => P(p, t));
      const n = pts.length;
      const w0 = b.w0 * unit, w1 = b.w1 * unit;
      const k = Math.max(2, Math.round(w0 / 2.4));
      ctx.strokeStyle = `rgba(${ink},${alpha})`;
      ctx.lineWidth = 0.7;
      ctx.beginPath();
      for (let j = 0; j < k; j++) {
        const f = k === 1 ? 0 : j / (k - 1) - 0.5;
        for (let i = 0; i < n; i++) {
          const a = pts[Math.max(0, i - 1)], c = pts[Math.min(n - 1, i + 1)];
          const dx = c[0] - a[0], dy = c[1] - a[1], L = Math.hypot(dx, dy) || 1;
          const w = w0 + ((w1 - w0) * i) / (n - 1);
          const x = pts[i][0] + (-dy / L) * f * w, y = pts[i][1] + (dx / L) * f * w;
          i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
      }
      ctx.stroke();
    }

    function dot(q, r, a) {
      const g = ctx.createRadialGradient(q[0], q[1], 0, q[0], q[1], r * 4);
      g.addColorStop(0, `rgba(255,255,255,${a})`);
      g.addColorStop(0.25, `rgba(255,255,255,${a * 0.6})`);
      g.addColorStop(1, "rgba(255,255,255,0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(q[0], q[1], r * 4, 0, 7); ctx.fill();
    }

    function frame(now) {
      const t = (now - t0) / 1000;
      const dt = Math.min(0.05, (now - (last || now)) / 1000);
      last = now;
      ctx.clearRect(0, 0, W, H);
      const s = P([0, 0], t), R = unit * 1.3;

      // sunburst rays behind the cell body
      ctx.strokeStyle = `rgba(${ink},0.16)`;
      ctx.lineWidth = 0.6;
      ctx.beginPath();
      for (let i = 0; i < 180; i++) {
        const th = (i / 180) * Math.PI * 2 + t * 0.01;
        const r0 = R * 1.25, r1 = R * (2.6 + 0.8 * Math.sin(i * 1.7));
        ctx.moveTo(s[0] + Math.cos(th) * r0, s[1] + Math.sin(th) * r0);
        ctx.lineTo(s[0] + Math.cos(th) * r1, s[1] + Math.sin(th) * r1);
      }
      ctx.stroke();

      for (const d of world.dendrites) {
        const dead = d.c && d.c.excluded;
        for (const b of d.branches) hatch(b, t, dead ? 0.22 : 0.9);
      }
      for (const b of world.extra) hatch(b, t, 0.75);
      // axon: a thin bundle with myelin sheaths drawn as outlined capsules
      const ap = world.axon.pts.map((p) => P(p, t));
      ctx.strokeStyle = `rgba(${ink},0.85)`; ctx.lineWidth = 0.7;
      for (const off of [-1.6, 0, 1.6]) {
        ctx.beginPath();
        ap.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1] + off) : ctx.moveTo(p[0], p[1] + off)));
        ctx.stroke();
      }
      for (let i = 2; i + 3 < ap.length; i += 4) {
        const a = ap[i], c = ap[i + 3];
        const mx = (a[0] + c[0]) / 2, my = (a[1] + c[1]) / 2, ang = Math.atan2(c[1] - a[1], c[0] - a[0]);
        const len = Math.hypot(c[0] - a[0], c[1] - a[1]) / 2;
        for (const sc of [1, 0.72]) {
          ctx.beginPath(); ctx.ellipse(mx, my, len * sc, unit * 0.22 * sc, ang, 0, 7); ctx.stroke();
        }
      }
      for (const b of world.terms) {
        hatch(b, t, 0.8);
        const e = P(b.pts[b.pts.length - 1], t);
        ctx.beginPath(); ctx.arc(e[0], e[1], unit * 0.16, 0, 7); ctx.stroke();
      }

      // cell body: concentric engraved rings, irregular rim, and the nucleus (the model)
      ctx.fillStyle = "rgba(0,10,80,0.2)";
      ctx.beginPath(); ctx.arc(s[0], s[1], R, 0, 7); ctx.fill();
      ctx.strokeStyle = `rgba(${ink},0.9)`; ctx.lineWidth = 0.7;
      for (let k = 0; k < 14; k++) {
        const rr = R * (1 - k * 0.05);
        ctx.beginPath();
        for (let i = 0; i <= 64; i++) {
          const th = (i / 64) * Math.PI * 2;
          const wob = 1 + 0.05 * Math.sin(th * 3 + 0.7 + k * 0.2) + 0.02 * Math.sin(th * 7 + t * 0.5);
          const x = s[0] + Math.cos(th) * rr * wob, y = s[1] + Math.sin(th) * rr * wob;
          i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
        ctx.stroke();
      }
      const nr = R * 0.36;
      ctx.fillStyle = `rgba(${ink},${0.75 + Math.min(glow, 1) * 0.25})`;
      ctx.beginPath(); ctx.arc(s[0] + R * 0.05, s[1] + R * 0.03, nr, 0, 7); ctx.fill();
      ctx.strokeStyle = "rgba(0,0,0,0.25)";
      ctx.beginPath();
      for (let i = -5; i <= 5; i++) {
        const y = s[1] + R * 0.03 + (i / 5) * nr * 0.8, half = Math.sqrt(Math.max(0, nr * nr - (y - s[1] - R * 0.03) ** 2));
        ctx.moveTo(s[0] + R * 0.05 - half * 0.2, y); ctx.lineTo(s[0] + R * 0.05 + half, y);
      }
      ctx.stroke();
      if (glow > 0.05) dot([s[0] + R * 0.05, s[1] + R * 0.03], nr * 0.5, Math.min(glow, 1) * 0.5);

      // signals
      if (!reduce) {
        for (const d of world.dendrites) {
          const dead = d.c && d.c.excluded;
          if (Math.random() < dt * (dead ? 0.35 : 0.6)) d.pulses.push({ s: 0, v: 0.2 + Math.random() * 0.1 });
          for (const p of d.pulses) {
            p.s += p.v * dt;
            const fade = dead ? Math.max(0, 1 - p.s / 0.45) : 1;
            if (fade > 0) dot(P(at(d.path, p.s), t), 2.2, 0.95 * fade);
          }
          if (!dead) glow = Math.min(1.6, glow + 0.45 * d.pulses.filter((p) => p.s >= 1).length);
          d.pulses = d.pulses.filter((p) => p.s < 1 && !(dead && p.s > 0.45));
        }
        if (glow > 0.9 && Math.random() < 0.35) { world.axon.pulses.push({ s: 0 }); glow -= 0.4; }
        for (const p of world.axon.pulses) { p.s += dt * 0.18; dot(P(at(world.axon, p.s), t), 2.4, 0.95); }
        world.axon.pulses = world.axon.pulses.filter((p) => p.s < 1);
        glow = Math.max(0, glow - dt * 0.5);
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
        const hw = el.offsetWidth / 2 + 6;
        el.style.left = `${Math.max(hw, Math.min(W - hw, ox + p[0] * unit))}px`;
        el.style.top = `${Math.max(el.offsetHeight * 1.4 + 4, Math.min(H - 8, oy + p[1] * unit))}px`;
        return el;
      };
      for (const d of world.dendrites) {
        if (!d.c) continue;
        const el = add(d.path.pts[0], d.c.html || `<b>${d.c.name}</b><span>${d.c.excluded ? "0% · excluded" : d.c.share}</span>`, (d.c.excluded ? "dead" : "") + (d.c.html ? " device" : ""));
        if (d.c.title) el.title = d.c.title;
      }
      if (opts.somaLabel) add([0, 2.05], opts.somaLabel, "soma");
      if (opts.axonLabel) add([world.axonEnd[0] + 0.1, world.axonEnd[1] + 1.15], opts.axonLabel, "axon");
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
      },
    };
  }

  window.AxonNeuron = { mount };
})();

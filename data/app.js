// AWM site: single-page app. The paper is the home page; the 25 games are linked from where the paper names them.
// All data comes from data/*.js written by build.py; this file only renders, decodes frames and navigates.
(function () {
  "use strict";
  var S = window.AWM_SITE;
  var app = document.getElementById("app");
  var GAMES = (S.games || []).map(function (g) { return g.g; });
  var INFO = {}; (S.games || []).forEach(function (g) { INFO[g.g] = g; });

  // ---------------------------------------------------------------- helpers
  function esc(s) {
    return String(s === undefined || s === null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function tok(s) { return String(s).replace(/[^A-Za-z0-9._~-]/g, "-"); }
  function table(head, rows, num) {
    num = num || [];
    return '<div class="tbox"><table class="t"><thead><tr>' + head.map(function (h) { return "<th>" + h + "</th>"; }).join("") +
      "</tr></thead><tbody>" + rows.map(function (r) {
        return "<tr>" + r.map(function (c, i) { return '<td class="' + (num.indexOf(i) >= 0 ? "n" : "") + '">' + (c === null || c === undefined ? "—" : c) + "</td>"; }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
  }
  function orig(zh, en) {
    if (!zh || zh === en) return "";
    return '<details class="orig"><summary>Original</summary><div>' + esc(zh) + "</div></details>";
  }
  var loaded = {};
  function load(src) {
    if (loaded[src]) return loaded[src];
    loaded[src] = new Promise(function (ok, bad) {
      var s = document.createElement("script");
      s.charset = "utf-8"; s.src = src; s.onload = function () { ok(); };
      s.onerror = function () { delete loaded[src]; bad(new Error("Could not load " + src)); };
      document.head.appendChild(s);
    });
    return loaded[src];
  }
  function loadGame(g) { return load("data/g-" + g + ".js").then(function () { return window.AWM_G[g]; }); }
  function typeset(node) {
    var go = function () { if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([node]).catch(function () {}); };
    if (window.MathJax && MathJax.typesetPromise) go();
    else { var n = 0, t = setInterval(function () { n++; if ((window.MathJax && MathJax.typesetPromise) || n > 100) { clearInterval(t); go(); } }, 100); }
  }
  function sources(list) {
    var li = list.filter(Boolean).map(function (x) { return "<li><code>" + esc(x) + "</code></li>"; }).join("");
    return '<footer class="site"><b>Files read for this page</b> (paths relative to the workspace root)<ul>' + li + "</ul>Built " + esc(S.built) + ".</footer>";
  }
  function scrollTo(id) {
    if (!id) { window.scrollTo(0, 0); return; }
    var el = document.getElementById(id);
    if (el) { if (el.tagName === "DETAILS") el.open = true; el.scrollIntoView(); } else window.scrollTo(0, 0);
  }
  function setNav(k) {
    Array.prototype.forEach.call(document.querySelectorAll("#nav a"), function (a) { a.classList.toggle("on", a.getAttribute("data-k") === k); });
  }

  // ---------------------------------------------------------------- theme
  (function () {
    var KEY = "awm-theme";
    try { var t = localStorage.getItem(KEY); if (t) document.documentElement.setAttribute("data-theme", t); } catch (e) {}
    var b = document.getElementById("theme");
    if (b) b.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme");
      if (!cur) cur = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      var nx = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nx);
      try { localStorage.setItem(KEY, nx); } catch (e) {}
    });
  })();

  // ---------------------------------------------------------------- frames
  function decodeFrames(R) {
    var N = R.recs.length, P = new Array(N), X = new Array(N);
    function full(o) { var a = new Uint8Array(o.w * o.h); for (var i = 0; i < a.length; i++) a[i] = parseInt(o.x.charAt(i), 16); return { w: o.w, h: o.h, a: a }; }
    function patch(b, d) { var a = b.a.slice(); for (var i = 0; i < d.length; i++) { var v = d[i]; a[v >> 4] = v & 15; } return { w: b.w, h: b.h, a: a }; }
    for (var i = 0; i < N; i++) {
      var r = R.recs[i], p;
      if (r.p === undefined || r.p === null) p = X[i - 1];
      else if (Array.isArray(r.p)) p = patch(X[i - 1], r.p);
      else p = full(r.p);
      P[i] = p; X[i] = Array.isArray(r.n) ? patch(p, r.n) : full(r.n);
    }
    return { P: P, X: X };
  }
  function palette(R) { return R.palette.map(function (h) { return [parseInt(h.substr(1, 2), 16), parseInt(h.substr(3, 2), 16), parseInt(h.substr(5, 2), 16)]; }); }
  function drawFrame(cv, f, pal, SC, changed, click) {
    cv.width = f.w * SC; cv.height = f.h * SC;
    var ctx = cv.getContext("2d"), img = ctx.createImageData(f.w * SC, f.h * SC), d = img.data, W = f.w * SC;
    for (var y = 0; y < f.h; y++) for (var x = 0; x < f.w; x++) {
      var c = pal[f.a[y * f.w + x]] || [0, 0, 0];
      for (var yy = 0; yy < SC; yy++) { var o = ((y * SC + yy) * W + x * SC) * 4; for (var xx = 0; xx < SC; xx++) { d[o] = c[0]; d[o + 1] = c[1]; d[o + 2] = c[2]; d[o + 3] = 255; o += 4; } }
    }
    ctx.putImageData(img, 0, 0);
    if (changed) {
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--changed") || "#f0a500"; ctx.lineWidth = Math.max(1, SC / 4);
      for (var k = 0; k < changed.length; k++) { var q = changed[k]; ctx.strokeRect((q % f.w) * SC + 1, Math.floor(q / f.w) * SC + 1, SC - 2, SC - 2); }
    }
    if (click) {
      [["#ffffff", 3], ["#e0303a", 1.5]].forEach(function (s) { ctx.strokeStyle = s[0]; ctx.lineWidth = s[1]; ctx.beginPath(); ctx.arc(click[0] * SC + SC / 2, click[1] * SC + SC / 2, SC * 1.6, 0, 7); ctx.stroke(); });
    }
  }

  // ---------------------------------------------------------------- home = the paper
  var PIPE = '<svg class="pipeline" viewBox="0 0 1000 210" role="img" aria-label="AWM pipeline: observe, Python hypotheses, objects and shared rules, Lean proof">' +
    '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="ah" d="M0,0 L10,5 L0,10 z"/></marker></defs>' +
    box(10, "1  Observe", ["act in the game and record", "every transition (frame,", "action, next frame)"]) +
    box(265, "2  Hypothesise in Python", ["each hypothesis is a function", "that judges every transition", "counterexample → revise / retire"]) +
    box(520, "3  Objects and shared rules", ["condense the hypotheses into", "typed objects (World / parse)", "and shared rules"]) +
    box(775, "4  Prove in Lean 4", ["rules become definitions;", "the kernel checks consistent,", "faithful, reachable / unreachable"]) +
    '<path class="ar" d="M225,90 L262,90" marker-end="url(#ah)"/><path class="ar" d="M480,90 L517,90" marker-end="url(#ah)"/><path class="ar" d="M735,90 L772,90" marker-end="url(#ah)"/>' +
    '<path class="ar" d="M372,150 C372,195 118,195 118,153" marker-end="url(#ah)"/><text class="sb" x="182" y="202">a bet fails or a counterexample appears: run an experiment</text></svg>';
  function box(x, h, lines) {
    return '<rect class="box" x="' + x + '" y="30" width="215" height="120" rx="4"/><text class="hd" x="' + (x + 14) + '" y="60">' + h + "</text>" +
      lines.map(function (l, i) { return '<text class="sb" x="' + (x + 14) + '" y="' + (86 + 18 * i) + '">' + l + "</text>"; }).join("");
  }
  function paperSections() { return ((S.paper || {}).sections) || []; }
  function secId(s) { var id = String(s.id || ""); return id.indexOf("paper.") === 0 ? id : "paper." + tok(id); }

  function exploreCard(g) {
    var i = INFO[g]; if (!i) return "";
    return '<div class="explore"><a href="#' + g + '"><img src="thumbs/' + g + '.png" alt="' + g + ', first frame"></a><div>' +
      "<b>" + g + "</b> · " + i.levels + "/" + i.level_count + " levels · " + i.steps + " actions · " + i.concepts + " hypotheses · score " + esc(i.score) +
      '<div class="links"><a href="#' + g + '.replay">Step-by-step replay</a><a href="#' + g + '.rules">Concept book</a><a href="#' + g + '.proof">Lean proof</a><a href="#' + g + '">Overview</a></div></div></div>';
  }
  function addExploreCards(root) {
    var done = {}, seen = {};                 // one card per game, after the first paragraph of the body that names it
    Array.prototype.forEach.call(root.querySelectorAll('section[id^="paper."]:not([id="paper.abstract"]):not([id="paper.references"])'), function (sec) {
      Array.prototype.forEach.call(sec.querySelectorAll("a[href]"), function (a) {
        var g = (a.getAttribute("href") || "").slice(1);
        if (GAMES.indexOf(g) < 0 || seen[g]) return;
        seen[g] = 1;
        var block = a.closest("p, li, figure, table, .tablewrap") || a.parentElement;
        while (block.parentElement && block.parentElement !== sec && !/^(P|FIGURE)$/.test(block.tagName)) block = block.parentElement;
        var d = document.createElement("div"); d.innerHTML = exploreCard(g);
        block.parentNode.insertBefore(d.firstChild, block.nextSibling);
        done[g] = 1;
      });
    });
    return done;
  }

  var heroTimer = null;
  function hero() {
    var g = S.featured;
    loadGame(g).then(function (D) {
      var cv = document.getElementById("hero-cv"); if (!cv) return;
      var R = D.replay, F = decodeFrames(R), pal = palette(R), i = 0, N = R.recs.length;
      var cap = document.getElementById("hero-cap");
      if (heroTimer) clearInterval(heroTimer);
      heroTimer = setInterval(function () {
        if (!document.getElementById("hero-cv")) { clearInterval(heroTimer); heroTimer = null; return; }
        var r = R.recs[i];
        drawFrame(cv, F.X[i], pal, 4, null, null);
        cap.innerHTML = "<b>" + g + "</b>, recorded run, step " + r.st + " of " + R.recs[N - 1].st + " · level " + r.l + " · <code>" + esc(r.a) + "</code> · " +
          '<a href="#' + g + ".replay." + r.s + '">open this step</a>';
        i = (i + 1) % N;
      }, 160);
    }).catch(function () {});
  }

  function home(anchor) {
    setNav(anchor === "games" || anchor === "compare" ? "games" : anchor === "data" ? "data" : "home");
    var P = S.paper || {};
    var secs = paperSections();
    var tiles = S.tiles.map(function (t) { return '<div class="stat"><div class="v">' + esc(t[0]) + '</div><div class="k">' + esc(t[1]) + "</div><p>" + esc(t[2]) + "</p></div>"; }).join("");
    var toc = '<a href="#paper.abstract">Abstract</a>' + secs.map(function (s) { return '<a href="#' + secId(s) + '">' + esc((s.number ? s.number + " " : "") + s.title) + "</a>"; }).join("") +
      (P.bib_html ? '<a href="#paper.references">References</a>' : "") + '<a href="#games">Appendix: the 25 games</a><a href="#data">Data and sources</a>';
    var cards = S.games.map(function (i) {
      var start = i.fresh ? "started from an empty book" : ("started with " + (i.init === null ? "—" : i.init) + " concepts");
      return '<a class="gcard" href="#' + i.g + '"><img src="thumbs/' + i.g + '.png" alt="' + i.g + ', first frame" loading="lazy">' +
        '<div class="t"><b>' + i.g + "</b><span>" + i.levels + "/" + i.level_count + " levels · " + i.steps + " actions</span>" +
        "<span>" + esc(start) + " · " + i.concepts + " concepts</span></div></a>";
    }).join("");
    var C = S.compare;
    var crow = C.rows.map(function (r) { return ['<a href="#' + r[0] + '"><code>' + r[0] + "</code></a>"].concat(r.slice(1).map(esc)); });
    app.innerHTML =
      '<section class="hero"><div><div class="kicker">ARC-AGI-3 · Python hypotheses · Lean 4</div>' +
      "<h1>" + esc(P.title || "Algebraic World Model") + "</h1>" +
      '<p class="lede">An agent plays a game it has never seen, writes each guess about the rules as a Python function checked against every recorded step, condenses the guesses into typed objects and shared rules, and proves in Lean 4 which levels can and cannot be won.</p>' +
      '<div class="btns"><a class="btn primary" href="#paper.abstract">Read the paper</a>' + (S.pdf ? '<a class="btn" href="' + S.pdf + '" target="_blank" rel="noopener">PDF</a>' : "") +
      '<a class="btn" href="#games">The 25 games</a></div></div>' +
      '<figure><div class="cvwrap"><canvas id="hero-cv"></canvas></div><figcaption id="hero-cap">Loading the replay…</figcaption></figure></section>' +
      '<div class="stats">' + tiles + "</div>" +
      '<div class="paperwrap"><nav class="toc" aria-label="Contents">' + toc + "</nav>" +
      '<article class="paper" id="paper">' +
      '<section id="paper.abstract"><h2>Abstract</h2>' + (P.abstract_html || "") + "</section>" +
      '<figure><figcaption>The loop the paper describes, as run on each game below.</figcaption>' + PIPE + "</figure>" +
      secs.map(function (s) { return '<section id="' + secId(s) + '"><h2>' + esc((s.number ? s.number + " " : "") + s.title) + "</h2>" + s.html + "</section>"; }).join("") +
      (P.bib_html ? '<section id="paper.references"><h2>References</h2><div class="bib">' + P.bib_html + "</div></section>" : "") +
      '<section id="games"><h2>Appendix: the 25 games</h2><p>Every public ARC-AGI-3 game, as the agent played it. Each game has the same five views: overview with the agent\'s own explanation, step-by-step replay, concept book, Lean proof, and the original workbench.</p>' +
      '<div class="gallery">' + cards + "</div>" +
      '<h3 id="compare">Official results on the same 25 games</h3><p>The first column is the scorecard of each sealed run; the other three are the per-game results published by ARC Prize (fetched ' + esc(C.fetched) + ").</p>" +
      table(C.head.map(esc), crow, [1, 2, 3, 4]) +
      '<ul class="note">' + C.conditions.map(function (c) { return "<li>" + esc(c) + "</li>"; }).join("") + "</ul>" +
      '<p class="note">Sources: ' + C.sources.map(function (u) { return '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + esc(u) + "</a>"; }).join(", ") + "</p></section>" +
      '<section id="data"><h2>Data and sources</h2>' + table(["What", "From"], [
        ["Frames of every step", "<code>bench/runs/&lt;run&gt;/transitions.jsonl</code>; each frame pair is checked against the sealed <code>formal/abstract.jsonl</code> by tid = sha1(action, frame, next frame)"],
        ["Reasoning at each step", "<code>bench/runs/&lt;run&gt;/reasoning.jsonl</code>, sent with each action"],
        ["Bets and journal lines", "the timeline of <code>bench/archive/&lt;seal&gt;/report/index.html</code>, generated from the journal"],
        ["The agent's explanation", "<code>bench/archive/&lt;seal&gt;/formal/…/explain.md</code>; the repaired-rule notes come from the header of <code>Game.lean</code>"],
        ["Concept book and its history", "<code>registry.json</code>, <code>concepts/*.py</code>, <code>model.json</code>"],
        ["Lean proof and check results", "<code>formal/Game.lean</code>, <code>formal/VERIFY.json</code>"],
        ["Scores, per-level actions, official replays", "<code>scorecard.json</code>, <code>MANIFEST.json</code>, <code>bench/ledger/games/&lt;game&gt;/analysis/official.json</code>"],
        ["How to play", "<code>bench/site/data/playguide.json</code> and its rule-checked revision"],
        ["Official results", "<code>bench/site/data/official_public_demo.json</code>"],
        ["Paper", "<code>paper-revision/main.tex</code>, the <code>sec/*.tex</code> it inputs, <code>Reference.bib</code>, figures (git " + esc(P.source_commit || "—") + ")"],
        ["Colour palette", "<code>" + esc(S.palette_src) + "</code>"]
      ]) + "</section>" +
      '<footer class="site">Built locally ' + esc(S.built) + ".</footer></article></div>";
    addExploreCards(document.getElementById("paper"));
    typeset(document.getElementById("paper"));
    hero();
    scrollTo(anchor && anchor !== "home" ? anchor : "");
  }

  // ---------------------------------------------------------------- one game: shared parts
  function gameNav(g, active) {
    var items = [["", "Overview"], ["replay", "Replay"], ["rules", "Concept book"], ["proof", "Lean proof"], ["wb", "Workbench (original)"]];
    return '<div class="btns">' + items.map(function (x) {
      return '<a class="btn' + (x[0] === active ? " primary" : "") + '" href="#' + g + (x[0] ? "." + x[0] : "") + '">' + x[1] + "</a>";
    }).join("") + "</div>";
  }
  function crumb(g, what) {
    return '<p class="crumb"><a href="#home">Paper</a> / <a href="#games">Games</a> / ' + (what ? '<a href="#' + g + '">' + g + "</a> / " + what : g) + "</p>";
  }
  function paperMentions(g) {
    var re = new RegExp('href="#' + g + '"');
    return paperSections().filter(function (s) { return re.test(s.html || ""); });
  }

  // ---------------------------------------------------------------- overview
  function overview(D) {
    var g = D.g, b = D.booklet;
    var bk = b.fresh ? "<p>The agent started from an empty concept book.</p>" :
      "<p>The book already held " + (b.init === null ? "—" : b.init) + " concepts when this run started. Origin of each concept's first version (from <code>registry.json</code>):</p>" +
      (b.origin.length ? table(["Run that wrote it", "Concepts", "Sealed as"], b.origin.map(function (o) {
        return ["<code>" + esc(o.run) + "</code>", o.n, o.seals.map(function (x) { return "<code>" + esc(x) + "</code>"; }).join(", ") || "—"];
      }), [1]) : "<p>—</p>") +
      b.plan.map(function (p) { return "<p><b>Plan for this run:</b> " + esc(p[0]) + "</p>" + orig(p[1], p[0]); }).join("");
    var ment = paperMentions(g);
    app.innerHTML = crumb(g) +
      '<h1 style="font-family:var(--mono);font-size:34px">' + g + "</h1>" +
      '<p class="lede">ARC-AGI-3 public game <code>' + esc(D.game) + "</code>, run <code>" + esc(D.run) + "</code>, sealed as <code>" + esc(D.seal) + "</code>.</p>" +
      gameNav(g, "") +
      (ment.length ? "<p>In the paper: " + ment.map(function (s) { return '<a href="#' + secId(s) + '">' + esc((s.number ? "§" + s.number + " " : "") + s.title) + "</a>"; }).join(", ") + "</p>" : "") +
      '<div class="rp"><div><h2 style="margin-top:8px">How to play</h2><p class="prose md">' + esc(D.playguide.en) + "</p>" + orig(D.playguide.zh, D.playguide.en) +
      "<h3>The concept book at the start</h3>" + bk + "</div>" +
      '<div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">' +
      '<figure style="margin:0"><figcaption class="note">Before the first recorded step</figcaption><img src="thumbs/' + g + '.png" alt="first frame" style="width:100%;image-rendering:pixelated;border-radius:3px"></figure>' +
      '<figure style="margin:0"><figcaption class="note">After the last recorded step</figcaption><img src="thumbs/' + g + '-last.png" alt="last frame" style="width:100%;image-rendering:pixelated;border-radius:3px"></figure>' +
      '</div><p><a class="btn primary" href="#' + g + '.replay">Open the replay</a></p></div></div>' +
      "<h2>Run summary</h2>" + table(["", ""], D.stats.map(function (r) { return [esc(r[0]), esc(r[1])]; })) +
      "<h3>Actions per level vs. human baseline (official scorecard)</h3>" + table(["Level", "Actions", "Human baseline", "Level score"], D.levels, [1, 2, 3]) +
      "<h3>Official replays</h3>" + table(["Part", "Records (seq)", "Count", "arcprize.org replay"], D.replays.map(function (r) {
        return [r.i, r.from + "–" + r.to, r.n, '<a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(r.url.split("/").pop().slice(0, 8)) + "… ↗</a>" + (r.cert ? ' <span class="chip ok">certified</span>' : "")];
      })) +
      "<h3>Published results of other systems on this game</h3>" + table(["System", "Score on this game (%)"], D.official.map(function (r) { return [esc(r[0]), esc(r[1])]; }).concat([["AWM (this run's scorecard)", esc(D.score)]])) +
      '<h2 id="' + g + '.explain">The agent\'s explanation</h2><p class="note">Written by the agent when it sealed the run (<code>explain.md</code>).</p>' +
      '<div class="md prose">' + (D.explain.en || "<p>—</p>") + "</div>" +
      (D.explain.zh ? '<details class="orig"><summary>Original</summary><div class="md" style="white-space:normal">' + D.explain.zh + "</div></details>" : "") +
      (D.notes.en ? '<h2 id="' + g + '.notes">Notes on the repaired rules (header of Game.lean)</h2><pre>' + esc(D.notes.en) + "</pre>" + orig(D.notes.zh, D.notes.en) : "") +
      sources(D.src);
    window.scrollTo(0, 0);
  }

  // ---------------------------------------------------------------- concept book
  function rules(D, arg) {
    var g = D.g;
    var alive = D.rules.filter(function (r) { return r.fate === "alive"; }).length;
    var nv = D.rules.reduce(function (a, r) { return a + r.vs.length; }, 0);
    var items = D.rules.map(function (r) {
      var last = r.vs[r.vs.length - 1] || {};
      var chips = '<span class="chip ' + (r.fate === "alive" ? "ok" : "bad") + '">' + (r.fate === "alive" ? "alive" : r.fate === "retired" ? "retired" : esc(r.fate)) + "</span>" +
        '<span class="chip">' + r.vs.length + (r.vs.length === 1 ? " version" : " versions") + "</span>" + (r.lean ? '<span class="chip con">in Game.lean</span>' : "") +
        (r.m ? '<span class="chip">speaks on ' + r.m[0] + " cells · right " + r.m[1] + " · wrong " + r.m[2] + "</span>" : "") +
        (r.fate === "retired" ? '<span class="chip bad">retired at step ' + r.rs + "</span>" : "");
      var vs = r.vs.map(function (v) {
        return '<div class="v"><div class="h">v' + v.v + ' · <a href="#' + g + ".replay.s" + v.st + '">step ' + v.st + "</a> · " + esc(v.at || "") + (v.run ? " · " + esc(v.run) : "") + " · " + v.ev + " evidence</div>" +
          '<div class="claim">' + esc(v.doc) + "</div>" + orig(v.doc_zh, v.doc) +
          (v.scope ? '<div class="note"><b>Scope:</b> ' + esc(v.scope) + "</div>" + orig(v.scope_zh, v.scope) : "") +
          (v.note ? '<div class="note"><b>Added in this version:</b> ' + esc(v.note) + "</div>" + orig(v.note_zh, v.note) : "") + "</div>";
      }).join("");
      return '<details class="item" id="' + g + ".rules." + tok(r.name) + '"><summary><span class="name">' + esc(r.name) + "</span> " + chips +
        '<div class="claim">' + esc(last.doc || "") + '</div></summary><div class="body"><div class="vers">' + vs + "</div>" +
        (r.src ? '<details class="item"><summary>Source as sealed (Python, as written)</summary><div class="body"><pre><code>' + esc(r.src) + "</code></pre></div></details>" : "") +
        "</div></details>";
    }).join("");
    app.innerHTML = crumb(g, "Concept book") + "<h1>" + g + " · concept book</h1>" +
      '<p class="lede">Every hypothesis the agent wrote while playing. Each is a Python function that judges every recorded transition TRUE, FALSE or stays silent. ' +
      D.rules.length + " concepts when sealed: " + alive + " alive, " + (D.rules.length - alive) + " retired, " + nv + " versions in all.</p>" +
      gameNav(g, "rules") +
      '<div class="btns"><button class="btn" type="button" id="xall">Expand all</button><button class="btn" type="button" id="call">Collapse all</button></div>' + items +
      (D.lib ? '<details class="item"><summary>Shared vocabulary <code>_lib.py</code> (as written)</summary><div class="body"><pre><code>' + esc(D.lib) + "</code></pre></div></details>" : "") +
      sources(D.src.slice(2, 6));
    document.getElementById("xall").onclick = function () { Array.prototype.forEach.call(app.querySelectorAll("details.item"), function (d) { d.open = true; }); };
    document.getElementById("call").onclick = function () { Array.prototype.forEach.call(app.querySelectorAll("details.item"), function (d) { d.open = false; }); };
    if (arg) scrollTo(g + ".rules." + tok(arg)); else window.scrollTo(0, 0);
  }

  // ---------------------------------------------------------------- Lean proof
  function proof(D) {
    var g = D.g, P = D.proof;
    var known = {}; D.rules.forEach(function (r) { known[r.name] = 1; });
    app.innerHTML = crumb(g, "Lean proof") + "<h1>" + g + " · Lean proof</h1>" +
      '<p class="lede">The learned rules are written as definitions in <code>stepRules</code>. The Lean kernel (<code>decide +kernel</code>) checks two theorems: <code>consistent</code>, every rule holds on every recorded transition; and <code>faithful</code>, computing with the rules from level 0 reproduces the whole winning route, each step equal to the recording.</p>' +
      gameNav(g, "proof") + "<h2>Check results</h2>" + table(["", ""], P.rows.map(function (r) { return [esc(r[0]), esc(r[1])]; })) +
      "<h2>Rules (" + P.names.length + ")</h2><p>" + P.names.map(function (n) {
        return known[n] ? '<a class="chip con" href="#' + g + ".rules." + tok(n) + '">' + esc(n) + "</a>" : '<span class="chip">' + esc(n) + "</span>";
      }).join("") + "</p>" +
      "<h2>Theorems</h2><p>" + P.thms.map(function (t) { return "<code>" + esc(t) + "</code> "; }).join("") + "</p>" +
      (D.notes.en ? "<h2>Notes in the file header</h2><pre>" + esc(D.notes.en) + "</pre>" + orig(D.notes.zh, D.notes.en) : "") +
      "<h2>Game.lean (source as written; generated data section omitted)</h2><pre><code>" + esc(P.view) + "</code></pre>" + sources([P.path]);
    window.scrollTo(0, 0);
  }

  // ---------------------------------------------------------------- workbench (original pages)
  var wbQuery = "";
  function wb(D, arg) {
    var g = D.g;
    load("data/wbidx-" + g + ".js").then(function () {
      var X = (window.AWM_WBIDX || {})[g];
      if (!X || !X.pages) { app.innerHTML = crumb(g, "Workbench") + "<p>—</p>"; return; }
      var i = Math.max(0, Math.min(X.pages.length - 1, parseInt(arg || "0", 10) || 0));
      var path = X.pages[i];
      return load("data/wb-" + g + "-" + X.chunk[i] + ".js").then(function () {
        var html = (window.AWM_WB || {})[g + ":" + X.chunk[i]][path];
        var q = wbQuery; wbQuery = "";
        html = html.replace(/location\.search/g, "(window.__Q||location.search)");
        var inject = "<script>window.__Q=" + JSON.stringify(q) + ";<\/script>";
        html = /<head[^>]*>/i.test(html) ? html.replace(/<head[^>]*>/i, function (m) { return m + inject; }) : inject + html;
        app.innerHTML = crumb(g, "Workbench") + "<h1>" + g + " · workbench</h1>" +
          '<p class="lede">The typed object layer (World / parse), the shared rules and the per-level Lean theorems, as the bench generated them (original pages, in Chinese). Page <code>' + esc(path) + "</code> (" + (i + 1) + " of " + X.pages.length + ").</p>" +
          gameNav(g, "wb") +
          '<details class="item"><summary>All pages (' + X.pages.length + ')</summary><div class="body pv-list">' +
          X.pages.map(function (p, k) { return '<a class="chip' + (k === i ? " con" : "") + '" href="#' + g + ".wb." + k + '">' + esc(p) + "</a>"; }).join("") + "</div></details>" +
          '<iframe class="wb-frame" id="wbf" title="Workbench page"></iframe>' + sources(["bench/ledger/games/" + g + "/web/dist/" + path]);
        var f = document.getElementById("wbf");
        f.addEventListener("load", function () {
          var d;
          try { d = f.contentDocument; } catch (e) { return; }
          if (!d) return;
          d.addEventListener("click", function (e) {
            var a = e.target.closest ? e.target.closest("a") : null;
            if (!a) return;
            var href = a.getAttribute("href") || "";
            if (/^(https?:|mailto:)/.test(href)) { a.setAttribute("target", "_blank"); a.setAttribute("rel", "noopener"); return; }
            if (!href || href.charAt(0) === "#") return;
            var parts = href.split("#")[0].split("?");
            var k = X.pages.indexOf(resolve(path, parts[0]));
            if (k < 0) k = X.pages.indexOf(parts[0].replace(/^(\.\/)+/, ""));
            if (k < 0) {
              var bn = parts[0].split("/").pop(), hits = X.pages.filter(function (p) { return p.split("/").pop() === bn; });
              if (hits.length === 1) k = X.pages.indexOf(hits[0]);
            }
            if (k < 0) return;
            e.preventDefault();
            wbQuery = parts[1] ? "?" + parts[1] : "";
            location.hash = g + ".wb." + k;
          }, true);
        });
        f.srcdoc = html;
        window.scrollTo(0, 0);
      });
    }).catch(function (e) { app.innerHTML = "<p>" + esc(e.message) + "</p>"; });
  }
  function resolve(cur, href) {
    var base = cur.split("/"); base.pop();
    href.split("/").forEach(function (s) { if (s === "..") base.pop(); else if (s && s !== ".") base.push(s); });
    var p = base.join("/");
    return p === "" ? "index.html" : p;
  }

  // ---------------------------------------------------------------- replay
  var RP = null;
  function replay(D, arg) {
    var g = D.g, R = D.replay, N = R.recs.length, SC = 8;
    app.innerHTML = crumb(g, "Replay") + "<h1>" + g + " · replay</h1>" +
      '<p class="lede">All ' + N + " recorded transitions of run <code>" + esc(D.run) + "</code>. Left: the frame before the action (a click is circled). Right: the frame after (changed cells are outlined). Beside them: what the agent was thinking at this step, and the bet and journal of its batch.</p>" +
      gameNav(g, "replay") +
      '<div class="rp"><div>' +
      '<div class="boards"><figure><figcaption>Before</figcaption><div class="cv"><canvas id="cv-prev"></canvas></div></figure>' +
      '<figure><figcaption>After</figcaption><div class="cv"><canvas id="cv-next"></canvas></div></figure></div>' +
      '<div class="ctrl"><button id="first" title="First">⏮</button><button id="prev" title="Previous step (←)">◀</button>' +
      '<button id="play" title="Play / pause (Space)">Play</button><button id="next" title="Next step (→)">▶</button><button id="last" title="Last">⏭</button>' +
      '<select id="speed" title="Speed"><option value="2">2 steps/s</option><option value="4" selected>4 steps/s</option><option value="10">10 steps/s</option><option value="30">30 steps/s</option></select>' +
      '<span id="pos" class="mono"></span></div>' +
      '<div class="ctrl"><input type="range" id="slider" min="0" value="0" aria-label="Position"></div>' +
      '<canvas id="strip" class="strip"></canvas>' +
      '<div class="legend"><span><i style="background:var(--ms)"></i>level cleared</span><span><i style="background:var(--warn)"></i>restart</span>' +
      '<span><i style="background:var(--bad)"></i>batch with a counterexample</span><span><i style="background:var(--con)"></i>batch that changed the book</span><span>alternating shades = levels</span></div>' +
      '<div class="ctrl"><select id="level"><option value="">Jump to a level…</option></select>' +
      '<button id="pb" title="Previous batch ([)">Previous batch</button><button id="nb" title="Next batch (])">Next batch</button>' +
      '<button id="nl">Next level change</button><button id="ncex">Next counterexample</button><button id="ncon">Next book change</button>' +
      '<label><input type="checkbox" id="hl" checked> outline changed cells</label></div>' +
      '<p class="note">Keys: <span class="kbd">←</span> <span class="kbd">→</span> step, <span class="kbd">Space</span> play, <span class="kbd">[</span> <span class="kbd">]</span> previous / next batch.</p>' +
      '</div><div><div class="pane"><h4>This step</h4><dl class="kv" id="info"></dl></div>' +
      '<div class="pane" id="why"></div><div class="pane" id="batch"></div></div></div>' +
      sources([D.replay_src.transitions, D.replay_src.reasoning, D.replay_src.report]);

    var F = decodeFrames(R), P = F.P, X = F.X, pal = palette(R);
    function diffCells(a, b) { if (a.w !== b.w || a.h !== b.h) return null; var out = []; for (var i = 0; i < a.a.length; i++) if (a.a[i] !== b.a[i]) out.push(i); return out; }
    function clickOf(act) { var m = /^ACTION6:(\d+),(\d+)/.exec(act || ""); return m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : null; }
    var B = R.batches || [];
    var bflag = B.map(function (b) { var f = { cex: false, con: false }; (b.lines || []).forEach(function (l) { if (l[0] === "cex") f.cex = true; if (l[0] === "con") f.con = true; }); return f; });
    var bFirst = B.map(function () { return -1; });
    for (var j = 0; j < N; j++) { var bj = R.recs[j].b; if (bj >= 0 && bFirst[bj] < 0) bFirst[bj] = j; }
    var firstB = bFirst.filter(function (x) { return x >= 0; })[0];
    var known = {}; D.rules.forEach(function (r) { known[r.name] = 1; });
    function chip(n) { return known[n] ? '<a class="chip con" href="#' + g + ".rules." + tok(n) + '">' + esc(n) + "</a>" : '<span class="chip">' + esc(n) + "</span>"; }
    function $(id) { return document.getElementById(id); }
    var cvP = $("cv-prev"), cvN = $("cv-next"), sl = $("slider"), strip = $("strip");
    sl.max = N - 1;
    var cur = 0, timer = null, lastB = -2;
    function linesHtml(lines) {
      return lines.map(function (l) {
        return '<li class="' + esc(l[0]) + '"><span class="tm">' + esc(l[1]) + '</span><span class="tg">' + esc(l[2]) + "</span> " + esc(l[3]) + orig(l[4], l[3]) + "</li>";
      }).join("");
    }
    function show(i) {
      cur = Math.max(0, Math.min(N - 1, i));
      var r = R.recs[cur], p = P[cur], x = X[cur];
      drawFrame(cvP, p, pal, SC, null, clickOf(r.a));
      drawFrame(cvN, x, pal, SC, $("hl").checked ? diffCells(p, x) : null, null);
      sl.value = cur; $("pos").textContent = (cur + 1) + " / " + N;
      var ev = [];
      if (r.L > r.l) ev.push('<span class="evt">level ' + r.l + " → " + r.L + "</span>");
      if (r.L < r.l) ev.push('<span class="evt">level number ' + r.l + " → " + r.L + "</span>");
      if (r.S && r.S !== "NOT_FINISHED") ev.push('<span class="evt">' + esc(r.S) + "</span>");
      if (/^RESET/.test(r.a)) ev.push("restart");
      $("info").innerHTML = "<dt>Record</dt><dd>seq " + r.s + " (step " + r.st + ")</dd><dt>Level</dt><dd>" + r.l + " (counting from 0)</dd>" +
        "<dt>Action</dt><dd><code>" + esc(r.a) + "</code></dd><dt>Frame diff</dt><dd>" + (r.d === null ? "frame size changed" : r.d + " cells") + "</dd>" +
        "<dt>Events</dt><dd>" + (ev.length ? ev.join("; ") : "—") + "</dd>";
      var w = "<h4>The agent at this step</h4>";
      if (r.i) {
        w += "<p>Step " + r.i[0] + " of " + r.i[1] + " in this batch." + (r.pc !== undefined ? " The model predicted " + r.pc + " cells" + (r.pk ? " (" + r.pk + " conflicting cells not bet)" : "") + "." : "") + "</p>";
        if (r.sp && r.sp.length) w += "<p>Based on " + r.sp.map(chip).join("") + "</p>";
        if (r.cl) w += '<ul class="note">' + Object.keys(r.cl).map(function (k) { return "<li><b>" + esc(k) + "</b>: " + esc(r.cl[k]) + orig((r.clz || {})[k], r.cl[k]) + "</li>"; }).join("") + "</ul>";
        if (r.ls) {
          var lsl = [["revised", r.ls.revised], ["registered", r.ls.registered], ["retired", r.ls.retired]].filter(function (x) { return x[1] && x[1].length; });
          w += '<details class="note"><summary>Last settle (after step ' + esc(r.ls.after_step) + "): " + esc(r.ls.concepts) + " concepts, " + esc(r.ls.counterexamples) + " counterexamples" +
            lsl.map(function (x) { return ", " + x[1].length + " " + x[0]; }).join("") + "</summary>" +
            lsl.map(function (x) { return "<ul>" + x[1].map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ul>"; }).join("") + "</details>";
        }
      } else {
        w += (r.pr ? "<p>Model prediction → hits: " + esc(r.pr) + "</p>" : "") + (r.sp && r.sp.length ? "<p>Concepts that spoke: " + r.sp.map(chip).join("") + "</p>" : "");
        if (!r.pr && !(r.sp && r.sp.length)) w += "<p>No concept spoke at this step.</p>";
      }
      $("why").innerHTML = w;
      if (r.b !== lastB) { showBatch(r.b); lastB = r.b; }
      drawStrip();
      try { history.replaceState(null, "", "#" + g + ".replay." + r.s); } catch (e) {}
    }
    function showBatch(bi) {
      var el = $("batch");
      if (bi < 0 || !B[bi]) {
        el.innerHTML = (firstB !== undefined && cur < firstB && R.pre.length) ? "<h4>Before the first batch</h4><ul class=\"lines\">" + linesHtml(R.pre) + "</ul>" : "<h4>Bet</h4><p>—</p>";
        return;
      }
      var b = B[bi], lines = linesHtml(b.lines || []);
      el.innerHTML = "<h4>" + esc(b.t) + " of " + B.length + (b.tm ? " · " + esc(b.tm) : "") + "</h4>" +
        (b.bet ? '<div class="bet"><b>Bet:</b> ' + esc(b.bet) + "</div>" + orig(b.bet_zh, b.bet) : "") +
        (lines ? '<div class="ctrl" style="margin:8px 0 0"><label><input type="checkbox" id="showchk"> show check and map lines</label></div><ul class="lines hidechk" id="lines">' + lines + "</ul>" : "");
      var c = $("showchk"); if (c) c.addEventListener("change", function () { $("lines").classList.toggle("hidechk", !c.checked); });
    }
    function drawStrip() {
      var dpr = window.devicePixelRatio || 1, w = Math.max(200, strip.clientWidth), h = 34;
      strip.width = w * dpr; strip.height = h * dpr;
      var ctx = strip.getContext("2d"); ctx.scale(dpr, dpr);
      var cs = getComputedStyle(document.documentElement), c1 = cs.getPropertyValue("--chip"), c2 = cs.getPropertyValue("--line");
      for (var px = 0; px < w; px++) { var i = Math.floor(px / w * N); ctx.fillStyle = (R.recs[i].l % 2) ? c2 : c1; ctx.fillRect(px, 10, 1, 16); }
      function tick(i, color, y0, y1) { ctx.fillStyle = color; ctx.fillRect(Math.round((i + 0.5) / N * w), y0, 2, y1 - y0); }
      for (var k = 0; k < N; k++) { var r = R.recs[k]; if (r.L > r.l) tick(k, cs.getPropertyValue("--ms"), 4, 32); else if (/^RESET/.test(r.a)) tick(k, cs.getPropertyValue("--warn"), 6, 30); }
      B.forEach(function (b, bi) { var k = bFirst[bi]; if (k < 0) return; if (bflag[bi].cex) tick(k, cs.getPropertyValue("--bad"), 0, 8); else if (bflag[bi].con) tick(k, cs.getPropertyValue("--con"), 0, 6); });
      ctx.fillStyle = cs.getPropertyValue("--ink"); ctx.fillRect(Math.round((cur + 0.5) / N * w) - 1, 0, 3, h);
    }
    strip.addEventListener("click", function (e) { var rc = strip.getBoundingClientRect(); stop(); show(Math.floor((e.clientX - rc.left) / rc.width * N)); });
    function find(from, dir, pred) { for (var i = from + dir; i >= 0 && i < N; i += dir) if (pred(i)) return i; return -1; }
    function jump(pred, dir) { var k = find(cur, dir || 1, pred); if (k >= 0) { stop(); show(k); } }
    function isBS(i) { var b = R.recs[i].b; return b >= 0 && bFirst[b] === i; }
    $("first").onclick = function () { stop(); show(0); }; $("prev").onclick = function () { stop(); show(cur - 1); };
    $("next").onclick = function () { stop(); show(cur + 1); }; $("last").onclick = function () { stop(); show(N - 1); };
    $("nb").onclick = function () { jump(isBS, 1); }; $("pb").onclick = function () { jump(isBS, -1); };
    $("nl").onclick = function () { jump(function (i) { return R.recs[i].L !== R.recs[i].l; }, 1); };
    $("ncex").onclick = function () { jump(function (i) { return isBS(i) && bflag[R.recs[i].b].cex; }, 1); };
    $("ncon").onclick = function () { jump(function (i) { return isBS(i) && bflag[R.recs[i].b].con; }, 1); };
    $("hl").onchange = function () { show(cur); };
    sl.oninput = function () { stop(); show(parseInt(sl.value, 10)); };
    var lv = $("level"), seenL = {};
    for (var q = 0; q < N; q++) { var L = R.recs[q].l; if (!seenL[L]) { seenL[L] = 1; var o = document.createElement("option"); o.value = q; o.textContent = "Start of level " + L; lv.appendChild(o); } }
    lv.onchange = function () { if (lv.value !== "") { stop(); show(parseInt(lv.value, 10)); } };
    function stop() { if (timer) { clearInterval(timer); timer = null; $("play").textContent = "Play"; } }
    $("play").onclick = function () {
      if (timer) { stop(); return; }
      $("play").textContent = "Pause";
      timer = setInterval(function () { if (cur >= N - 1) { stop(); return; } show(cur + 1); }, 1000 / (parseFloat($("speed").value) || 4));
    };
    $("speed").onchange = function () { if (timer) { stop(); $("play").click(); } };
    function seek(a) {
      // "<seq>" or "s<step>"
      var bystep = /^s\d+$/.test(a), v = parseInt(bystep ? a.slice(1) : a, 10), key = bystep ? "st" : "s";
      for (var t = 0; t < N; t++) if (R.recs[t][key] >= v) { show(t); return; }
      show(N - 1);
    }
    RP = {
      g: g, stop: stop, seek: seek,
      key: function (e) {
        if (e.key === "ArrowRight") { stop(); show(cur + 1); e.preventDefault(); }
        else if (e.key === "ArrowLeft") { stop(); show(cur - 1); e.preventDefault(); }
        else if (e.key === " ") { $("play").click(); e.preventDefault(); }
        else if (e.key === "]") jump(isBS, 1); else if (e.key === "[") jump(isBS, -1);
      }, resize: drawStrip
    };
    window.scrollTo(0, 0);
    if (arg) seek(arg); else show(0);
  }
  document.addEventListener("keydown", function (e) {
    if (!RP || (e.target && /INPUT|SELECT|TEXTAREA/.test(e.target.tagName))) return;
    RP.key(e);
  });
  window.addEventListener("resize", function () { if (RP) RP.resize(); });

  // ---------------------------------------------------------------- routing
  var HOME_ANCHORS = ["home", "games", "compare", "data"];
  var current = "";
  function route() {
    var h = decodeURIComponent(location.hash.replace(/^#/, ""));
    var parts = h.split(".");
    var head = parts[0] || "home";
    if (RP && head === RP.g && parts[1] === "replay" && current === RP.g + ".replay") {
      if (parts[2]) RP.seek(parts.slice(2).join("."));
      return;
    }
    if (RP) { RP.stop(); RP = null; }
    if (head === "paper") {                     // a place inside the paper on the home page
      if (current !== "home") { current = "home"; home(""); }
      scrollTo(h === "paper" ? "paper.abstract" : h);
      return;
    }
    if (GAMES.indexOf(head) >= 0) {
      var view = parts[1] || "", arg = parts.slice(2).join(".");
      current = head + "." + view;
      setNav("games");
      app.innerHTML = crumb(head) + '<p class="muted">Loading…</p>';
      loadGame(head).then(function (D) {
        if (view === "replay") replay(D, arg);
        else if (view === "rules") rules(D, arg);
        else if (view === "proof") proof(D);
        else if (view === "wb") wb(D, arg);
        else if (view === "explain" || view === "notes") { overview(D); scrollTo(head + "." + view); }
        else overview(D);
      }).catch(function (e) { app.innerHTML = "<p>" + esc(e.message) + "</p>"; });
      return;
    }
    var anchor = HOME_ANCHORS.indexOf(head) >= 0 ? head : "home";
    if (current === "home") { setNav(anchor === "home" ? "home" : anchor === "data" ? "data" : "games"); scrollTo(anchor === "home" ? "" : anchor); return; }
    current = "home";
    home(anchor);
  }
  window.addEventListener("hashchange", route);
  route();
})();

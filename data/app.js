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
  // The three stages of §1 and §2, in the paper's own names.
  var PIPE = '<svg class="pipeline" viewBox="0 0 1000 190" role="img" aria-label="AWM in three stages: Explore and Prototype, Structure and Simplify, Formalize and Prove">' +
    '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="ah" d="M0,0 L10,5 L0,10 z"/></marker></defs>' +
    box(10, "1  Explore & Prototype", ["explore the environment;", "build and revise an executable", "model from observed transitions"]) +
    box(350, "2  Structure & Simplify", ["typed objects and rules,", "simplified by four transformations", "that keep tested distinctions"]) +
    box(690, "3  Formalize & Prove", ["encode the model in Lean 4;", "kernel-checked proofs of", "reachability or impossibility"]) +
    '<path class="ar" d="M310,90 L347,90" marker-end="url(#ah)"/><path class="ar" d="M650,90 L687,90" marker-end="url(#ah)"/></svg>';
  function box(x, h, lines) {
    return '<rect class="box" x="' + x + '" y="30" width="300" height="120" rx="4"/><text class="hd" x="' + (x + 14) + '" y="60">' + esc(h) + "</text>" +
      lines.map(function (l, i) { return '<text class="sb" x="' + (x + 14) + '" y="' + (86 + 18 * i) + '">' + l + "</text>"; }).join("");
  }
  function provenance() {
    var D = S.data || {}, P = S.paper || {};
    return "Paper text at commit " + esc(P.source_commit || "—") + " (the PDF is built from the same commit) · data commit " + esc(D.commit || "—") +
      (D.date ? " (" + esc(D.date) + ")" : "") + " · built " + esc(S.built);
  }
  function paperSections() { return ((S.paper || {}).sections) || []; }
  function secId(s) { var id = String(s.id || ""); return id.indexOf("paper.") === 0 ? id : "paper." + tok(id); }

  function exploreCard(g) {
    var i = INFO[g]; if (!i) return "";
    return '<div class="explore"><a href="#' + g + '"><img src="thumbs/' + g + '.png" alt="' + g + ', first frame"></a><div>' +
      "<b>" + g + "</b> · " + i.levels + "/" + i.level_count + " levels · " + i.steps + " actions · " + i.concepts + " concepts · score " + esc(i.score) +
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

  // ---------------------------------------------------------------- C1: Figure 1, one part at a time (§1, §2)
  // Boxes are in the points of figure-1-awm-process-v13 (396 × 176 pt page; content ends at 145 pt).
  var STEPS = [
    [58, 36, 43, 31, "Explore & Prototype", "The agent presses a button in a game it has never seen."],
    [2, 23, 156, 66, "Explore & Prototype", "It records the transition: the frame before and the frame after."],
    [0, 97, 160, 48, "Explore & Prototype", "Each hypothesis is a Python program checked against every recorded transition; one that a transition contradicts is revised."],
    [165, 21, 113, 38, "Structure & Simplify", "Four transformations, inspired by projective and inductive limits, simplify object types and rules."],
    [165, 68, 114, 78, "Structure & Simplify", "The result is an algebraic world model: typed objects, rules w, a → w′, and a goal predicate."],
    [284, 67, 111, 38, "Formalize & Prove", "In Lean 4, a winning witness proves that a level can be won."],
    [284, 109, 111, 38, "Formalize & Prove", "An invariant or a cost bound proves that no legal winning sequence exists."]
  ];
  var heroTimer = null;
  function teaser() {
    return '<figure class="teaser"><svg id="t-svg" viewBox="0 0 396 147" role="img" aria-label="Figure 1 of the paper, highlighted one part at a time">' +
      '<defs><mask id="t-mask"><rect x="0" y="0" width="396" height="147" fill="#fff"/><rect id="t-hole" rx="3" fill="#000"/></mask></defs>' +
      '<image href="' + esc((S.figs || {}).steps) + '" x="0" y="0" width="396" height="176"/>' +
      '<rect class="t-dim" x="0" y="0" width="396" height="147" mask="url(#t-mask)"/><rect id="t-ring" class="t-ring" rx="3"/></svg>' +
      '<figcaption><b id="t-stage"></b> <span id="t-text"></span><span class="t-ctrl"><button type="button" id="t-play" class="btn">Pause</button> ' +
      '<span id="t-dots"></span></span><span class="note">Figure 1 of the paper, one part at a time (§1, §2).</span></figcaption></figure>';
  }
  function heroAnim() {
    var k = 0, dots = document.getElementById("t-dots");
    if (!dots) return;
    dots.innerHTML = STEPS.map(function (s, i) { return '<button type="button" class="t-dot" data-i="' + i + '" aria-label="Part ' + (i + 1) + '"></button>'; }).join("");
    function show(i) {
      k = (i + STEPS.length) % STEPS.length;
      var s = STEPS[k];
      ["t-hole", "t-ring"].forEach(function (id) {
        var r = document.getElementById(id); if (!r) return;
        r.setAttribute("x", s[0]); r.setAttribute("y", s[1]); r.setAttribute("width", s[2]); r.setAttribute("height", s[3]);
      });
      document.getElementById("t-stage").textContent = s[4] + ".";
      document.getElementById("t-text").textContent = s[5];
      Array.prototype.forEach.call(dots.children, function (b, j) { b.classList.toggle("on", j === k); });
    }
    function stop() { if (heroTimer) { clearInterval(heroTimer); heroTimer = null; } document.getElementById("t-play").textContent = "Play"; }
    function play() {
      stop(); document.getElementById("t-play").textContent = "Pause";
      heroTimer = setInterval(function () { if (!document.getElementById("t-svg")) { clearInterval(heroTimer); heroTimer = null; return; } show(k + 1); }, 1500);
    }
    document.getElementById("t-play").onclick = function () { if (heroTimer) stop(); else play(); };
    dots.onclick = function (e) { var b = e.target.closest("[data-i]"); if (b) { stop(); show(parseInt(b.getAttribute("data-i"), 10)); } };
    show(0);
    var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (still) stop(); else play();
  }

  // ---------------------------------------------------------------- C2: which caps each judgment gets right (§4.2, Figure 4)
  // Three numbers from the paper: engine optimum 19, AWM's proved bound 19, GPT-6 Astra's claimed bound 22. A cap c admits a win iff c ≥ the least winning cost.
  function capWidget() {
    return '<div class="pane capw"><h4>Drag the budget cap</h4><div class="ctrl"><input type="range" id="cap" min="18" max="22" step="1" value="18" aria-label="Budget cap">' +
      '<span class="mono" id="cap-v"></span></div><div class="tbox"><table class="t" id="cap-t"></table></div>' +
      '<p class="note">The sealed level uses cap 18. The engine wins at a cap of 19 or more. Each judgment below says “winnable” exactly when the cap is at least the minimum cost it reports. ' +
      "GPT-6 Astra's 22 would wrongly rule out wins that cost 19 to 21 (§1).</p></div>";
  }
  function capInit() {
    var el = document.getElementById("cap"); if (!el) return;
    var rows = [["Engine (ground truth)", 19], ["AWM (proved in Lean)", 19], ["GPT-6 Astra (claimed)", 22]];
    function upd() {
      var c = parseInt(el.value, 10), truth = c >= 19;
      document.getElementById("cap-v").textContent = "cap = " + c + (c === 18 ? " (sealed)" : "");
      document.getElementById("cap-t").innerHTML = "<thead><tr><th>Who</th><th>Minimum cost</th><th>Says at this cap</th><th></th></tr></thead><tbody>" +
        rows.map(function (r, i) {
          var says = c >= r[1];
          var ok = says === truth;
          return "<tr><td>" + r[0] + '</td><td class="n">' + r[1] + "</td><td>" + (says ? "winnable" : "impossible") + "</td><td>" +
            (i === 0 ? "" : '<span class="chip ' + (ok ? "ok" : "bad") + '">' + (ok ? "✓ correct" : "✗ wrong") + "</span>") + "</td></tr>";
        }).join("") + "</tbody>";
    }
    el.oninput = upd; upd();
  }

  function bibtex() {
    return '<section id="bibtex"><h2>BibTeX</h2><pre id="bib-text"><code>' + esc(S.bibtex) + '</code></pre>' +
      '<div class="btns"><button type="button" class="btn" id="bib-copy">Copy BibTeX</button><span class="note" id="bib-ok"></span></div></section>';
  }
  function bibInit() {
    var b = document.getElementById("bib-copy"); if (!b) return;
    b.onclick = function () {
      var t = S.bibtex, ok = document.getElementById("bib-ok");
      function fallback() {
        var r = document.createRange(); r.selectNodeContents(document.getElementById("bib-text"));
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); ok.textContent = "Selected; press Ctrl+C.";
      }
      try { navigator.clipboard.writeText(t).then(function () { ok.textContent = "Copied."; }, fallback); } catch (e) { fallback(); }
    };
  }

  function repro() {
    var rows = S.games.map(function (i) {
      return ['<a href="#' + i.g + '.proof"><code>' + i.g + "</code></a>", i.lean_ok ? '<span class="chip ok">pass</span>' : '<span class="chip bad">—</span>',
        i.lean_s === null || i.lean_s === undefined ? "—" : esc(i.lean_s) + " s", esc((i.axioms || []).join(", ") || "—"),
        "<code>" + esc(String(i.lean_sha || "—")) + "</code>"];
    });
    return '<section id="repro"><h2>Reproducibility</h2>' +
      "<p>The paper's statement is in its <a href=\"#paper.Reproducibility-statement\">Reproducibility statement</a>: one command per game regenerates the model, tests and Lean project; the per-game Lean projects are checked with Lean 4.34.0. " +
      "Below, the sealed <code>Game.lean</code> of each game shown on this site, the local kernel check recorded in its <code>VERIFY.json</code>, and its sha256. Check it with <code>python ledger/lean_check.py &lt;formal directory&gt;</code> in the bench repository.</p>" +
      table(["Game", "Kernel check", "Time", "Axioms", "Game.lean sha256"], rows, [2]) + "</section>";
  }

  function faq() {
    return '<section id="faq"><h2>Questions about the impossibility proofs</h2>' + (S.faq || []).map(function (f, i) {
      return '<details class="item" id="faq.' + (i + 1) + '"><summary>' + esc(f[0]) + '</summary><div class="body prose">' + f[1] + "</div></details>";
    }).join("") + "</section>";
  }

  function home(anchor) {
    setNav(anchor === "games" || anchor === "compare" ? "games" : anchor === "data" ? "data" : "home");
    var P = S.paper || {};
    var secs = paperSections();
    var tiles = S.tiles.map(function (t) { return '<div class="stat"><div class="v">' + esc(t[0]) + '</div><div class="k">' + esc(t[1]) + "</div><p>" + esc(t[2]) + "</p></div>"; }).join("");
    var toc = '<a href="#results">Main result</a><a href="#paper.abstract">Abstract</a>' + secs.map(function (s) { return '<a href="#' + secId(s) + '">' + esc((s.number ? s.number + " " : "") + s.title) + "</a>"; }).join("") +
      (P.bib_html ? '<a href="#paper.references">References</a>' : "") + '<a href="#games">Appendix: the 25 games</a><a href="#data">Data and sources</a>' +
      '<a href="#repro">Reproducibility</a><a href="#faq">Questions</a><a href="#autorepair">Autonomous repair (preliminary)</a><a href="#bibtex">BibTeX</a>';
    var T = S.tables || {};
    var results = '<section id="results"><h2>Main result: proving impossibility</h2>' +
      "<p>Two levels of <code>sc25</code> are sealed one unit below their minimum winning cost. The question is whether any legal winning sequence remains (§4 of the paper).</p>" +
      '<figure class="paper-figure"><img src="' + esc((S.figs || {}).l4) + '" alt="GPT-6 Astra claims a minimum cost of 22 on sealed sc25 level 4; AWM proves 19 in Lean." loading="lazy">' +
      '<figcaption class="paper-caption">Figure 4 of the paper. <a href="#paper.fig-l4attempts">Read its caption in the paper</a>.</figcaption></figure>' +
      capWidget() + (T["tab:verdicts"] || "") +
      '<p class="note">More: <a href="#faq">questions about the proofs</a>, the <a href="#sc25">sc25 game</a> as played, and how <a href="#lp85.merge">eleven lp85 concepts became one rule</a> (§2.5).</p></section>';
    var cards = S.games.map(function (i) {
      var start = i.fresh ? "started from an empty book" : ("started with " + (i.init === null ? "—" : i.init) + " concepts");
      return '<a class="gcard" href="#' + i.g + '"><img src="thumbs/' + i.g + '.png" alt="' + i.g + ', first frame" loading="lazy">' +
        '<div class="t"><b>' + i.g + "</b><span>" + i.levels + "/" + i.level_count + " levels · " + i.steps + " actions</span>" +
        "<span>" + esc(start) + " · " + i.concepts + " concepts</span></div></a>";
    }).join("");
    var C = S.compare;
    var crow = C.rows.map(function (r) { return ['<a href="#' + r[0] + '"><code>' + r[0] + "</code></a>"].concat(r.slice(1).map(esc)); });
    app.innerHTML =
      '<section class="hero"><div class="h-text"><div class="kicker">ARC-AGI-3 · Python hypotheses · Lean 4</div>' +
      "<h1>" + esc(P.title || "Algebraic World Model") + "</h1>" +
      '<p class="authors">Anonymous authors · Under review at ICLR 2027</p>' +
      '<p class="tldr"><b>TL;DR</b> ' + esc(S.tldr) + "</p>" +
      '<p class="lede">An agent plays a game it has never seen, writes each guess about the rules as a Python function checked against every recorded step, simplifies the guesses into typed objects and shared rules, and proves in Lean 4 which levels can and cannot be won.</p>' +
      '<div class="btns"><a class="btn primary" href="#paper.abstract">Read the paper</a>' + (S.pdf ? '<a class="btn" href="' + S.pdf + '" target="_blank" rel="noopener">Paper (PDF)</a>' : "") +
      (S.supplement ? '<a class="btn" href="' + S.supplement + '" target="_blank" rel="noopener">Supplementary (PDF)</a>' : "") +
      '<a class="btn" href="#games">The 25 games</a><a class="btn" href="#bibtex">BibTeX</a></div></div>' +
      '<div class="h-fig">' + teaser() + '<p class="note"><a href="#' + esc(S.featured) + '.replay">Watch a recorded run</a> step by step.</p></div>' +
      '<div class="stats h-stats">' + tiles + "</div></section>" +
      '<div class="paperwrap"><nav class="toc" aria-label="Contents">' + toc + "</nav>" +
      '<article class="paper" id="paper">' + results +
      '<p class="note">' + provenance() + ".</p>" +
      '<section id="paper.abstract"><h2>Abstract</h2>' + (P.abstract_html || "") + "</section>" +
      '<figure><figcaption>The loop the paper describes, as run on each game below.</figcaption>' + PIPE + "</figure>" +
      secs.map(function (s) { return '<section id="' + secId(s) + '"><h2>' + esc((s.number ? s.number + " " : "") + s.title) + "</h2>" + s.html + "</section>"; }).join("") +
      (P.bib_html ? '<section id="paper.references"><h2>References</h2><div class="bib">' + P.bib_html + "</div></section>" : "") +
      '<section id="games"><h2>Appendix: the 25 games</h2><p>Every public ARC-AGI-3 game, as the agent played it. Each game has the same five views: overview with the agent\'s own explanation, step-by-step replay, concept book, Lean proof, and the original workbench.</p>' +
      '<p class="note">In 22 games the certified clear followed uncertified sessions of the same run (Table 1). In ' + esc(S.inherited) + " games the sealed run started from a concept book written by an earlier run of the same game; those cards say how many concepts it started with, and each game's overview lists the run that wrote them. The other " + esc(GAMES.length - S.inherited) + " started from an empty book.</p>" +
      '<div class="gallery">' + cards + "</div>" +
      '<h3 id="compare">Official results on the same 25 games</h3><p>Table 1 of the paper:</p>' + ((S.tables || {})["tab:scores"] || "") +
      '<p>Per game: the first column is the scorecard of each sealed run; the other three are the per-game results published by ARC Prize (fetched ' + esc(C.fetched) + ").</p>" +
      table(C.head.map(esc), crow, [1, 2, 3, 4]) +
      '<ul class="note">' + C.conditions.map(function (c) { return "<li>" + esc(c) + "</li>"; }).join("") + "</ul>" +
      '<p class="note">Sources: ' + C.sources.map(function (u) { return '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + esc(u) + "</a>"; }).join(", ") + "</p></section>" +
      '<section id="data"><h2>Data and sources</h2><p>Table 2 of the paper:</p>' + ((S.tables || {})["tab:lean"] || "") +
      "<p>Figures and tables on this site are read from commit <code>" + esc((S.data || {}).commit) + "</code>" + ((S.data || {}).date ? " (" + esc(S.data.date) + ")" : "") +
      ", the build reported in the paper; the game data in <code>archive/</code>, <code>ledger/games/</code> and <code>site/data/</code> is unchanged up to the bench commit <code>" + esc((S.data || {}).head) + "</code> this site was built from.</p>" +
      table(["What", "From"], [
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
      ]) + "</section>" + repro() + faq() +
      '<section id="autorepair-link"><h2>Autonomous repair (preliminary)</h2><p>Runs that build the audit into the method, with no external signal that a bound is wrong, are on <a href="#autorepair">their own page</a>. They are reported in the supplementary material, not in the six-run evaluation.</p></section>' +
      bibtex() +
      '<footer class="site">' + provenance() + ".</footer></article></div>";
    addExploreCards(document.getElementById("paper"));
    typeset(document.getElementById("paper"));
    heroAnim(); capInit(); bibInit();
    scrollTo(anchor && anchor !== "home" ? anchor : "");
  }

  // ---------------------------------------------------------------- C9: autonomous repair (supplementary material, Appendix C.22)
  function autorepair() {
    setNav("home");
    app.innerHTML = '<p class="crumb"><a href="#home">Paper</a> / Autonomous repair</p><h1>Autonomous repair (preliminary)</h1>' +
      '<p class="lede">Preliminary; reported in the supplementary material, not in the six-run evaluation.</p>' +
      "<p>These pilots build the audit into the initial procedure, with no external signal that the bound is wrong. They are separate from both the six main runs and the four-attempt feedback repairs of §4.3. " +
      "The table is Appendix C.22 of the supplementary material; it separates numerical outcomes, the subject's own proof reports and independent rebuilding.</p>" +
      table(["Record", "Numerical outcome", "Proof verification"], (S.autorepair || []).map(function (r) { return r.map(esc); })) +
      "<p>The two phase2 pilots each restarted the dialogue session once while keeping their workspace files, so they are not uninterrupted-session replications. " +
      "These versions, interruptions and verification statuses do not define a common sampling protocol or a pooled success rate (Appendix C.22).</p>" +
      (S.supplement ? '<p><a class="btn" href="' + S.supplement + '" target="_blank" rel="noopener">Supplementary material (PDF)</a></p>' : "") +
      '<footer class="site">Source: <code>paper-revision/supplement/sec/92-appendix-c-sc25.tex</code>, §C.22 · ' + provenance() + ".</footer>";
    window.scrollTo(0, 0);
  }

  // ---------------------------------------------------------------- C4: how eleven lp85 concepts became press_permutes (§2.5, Figure 3)
  function mergeView(D) {
    var M = S.lp85_merge; if (!M || D.g !== "lp85") return "";
    var maxSt = 1;
    D.replay.recs.forEach(function (r) { if (r.st > maxSt) maxSt = r.st; });
    M.from.forEach(function (c) { c.vs.forEach(function (v) { if (v.st > maxSt) maxSt = v.st; }); if (c.rs > maxSt) maxSt = c.rs; });
    var W = 640, X0 = 150, H = 22, top = 24, n = M.from.length;
    function x(st) { return X0 + (W - X0 - 20) * (st || 0) / maxSt; }
    var svg = '<svg class="merge" viewBox="0 0 ' + (W + 170) + " " + (top + n * H + 40) + '" role="img" aria-label="When each of the eleven concepts was written, revised and withdrawn, and their merge into press_permutes">';
    svg += '<line class="ax" x1="' + X0 + '" y1="' + (top + n * H + 6) + '" x2="' + (W - 20) + '" y2="' + (top + n * H + 6) + '"/>' +
      '<text class="lb" x="' + X0 + '" y="' + (top + n * H + 22) + '">step 0</text><text class="lb" x="' + (W - 20) + '" y="' + (top + n * H + 22) + '" text-anchor="end">step ' + maxSt + "</text>";
    M.from.forEach(function (c, i) {
      var y = top + i * H, sameRun = function (v) { return v.run === D.run; };
      var st0 = c.vs.length ? c.vs[0].st : 0, end = c.fate === "retired" && c.rs ? c.rs : maxSt;
      svg += '<text class="nm" x="' + (X0 - 8) + '" y="' + (y + 4) + '" text-anchor="end">' + esc(c.name) + "</text>" +
        '<line class="life" x1="' + x(st0) + '" y1="' + y + '" x2="' + x(end) + '" y2="' + y + '"/>';
      c.vs.forEach(function (v) {
        var dot = '<circle class="v" cx="' + x(v.st) + '" cy="' + y + '" r="4"><title>v' + v.v + " written at step " + v.st + "</title></circle>";
        svg += sameRun(v) ? '<a href="#lp85.replay.s' + v.st + '">' + dot + "</a>" : dot;
      });
      if (c.fate === "retired" && c.rs) svg += '<text class="x" x="' + x(c.rs) + '" y="' + (y + 4) + '" text-anchor="middle">×<title>withdrawn at step ' + c.rs + "</title></text>";
      svg += '<path class="to" d="M' + (W - 14) + "," + y + " C" + (W + 30) + "," + y + " " + (W + 30) + "," + (top + n * H / 2 - H / 2) + " " + (W + 52) + "," + (top + n * H / 2 - H / 2) + '"/>';
    });
    svg += '<text class="rule" x="' + (W + 56) + '" y="' + (top + n * H / 2 - H / 2 + 4) + '">' + esc(M.rule) + "</text></svg>";
    return '<h2 id="lp85.merge">How eleven concepts became one rule</h2>' +
      "<p>During play the agent wrote the eleven concepts below for four button mechanisms: belts, stars, hubs and panels. Each dot is a version, placed at the play step where it was written (click one in this run to open that step)" +
      (M.from.some(function (c) { return c.fate === "retired"; }) ? "; × marks a withdrawal. " : "; none of the eleven was withdrawn during play. ") +
      "Generalization then replaces all eleven with one shared operation, <code>press_permutes</code>, parameterized by the pressed button. The unified rule preserves all 55 diagnostic rejections of the original concepts and detects 21 additional invalid transitions (§2.5, Figure 3).</p>" +
      '<div class="tbox" style="padding:8px">' + svg + "</div>" +
      '<p class="note">Concept names and merge sources: <code>' + esc(M.src) + "</code> (field <code>rules.press_permutes.from</code>); versions and steps: <code>bench/ledger/games/lp85/registry.json</code>.</p>";
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
      mergeView(D) + sources(D.src);
    window.scrollTo(0, 0);
  }

  // ---------------------------------------------------------------- concept book
  function rules(D, arg) {
    var g = D.g;
    var alive = D.rules.filter(function (r) { return r.fate === "alive"; }).length;
    var nv = D.rules.reduce(function (a, r) { return a + r.vs.length; }, 0);
    var items = D.rules.map(function (r) {
      var last = r.vs[r.vs.length - 1] || {};
      var chips = '<span class="chip ' + (r.fate === "alive" ? "ok" : "bad") + '">' + (r.fate === "alive" ? "alive" : r.fate === "retired" ? "withdrawn" : esc(r.fate)) + "</span>" +
        '<span class="chip">' + r.vs.length + (r.vs.length === 1 ? " version" : " versions") + "</span>" + (r.lean ? '<span class="chip con">in Game.lean</span>' : "") +
        (r.m ? '<span class="chip">speaks on ' + r.m[0] + " cells · right " + r.m[1] + " · wrong " + r.m[2] + "</span>" : "") +
        (r.fate === "retired" ? '<span class="chip bad">withdrawn at step ' + r.rs + "</span>" : "");
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
      '<p class="lede">Every concept the agent wrote while playing. Each is a Python hypothesis that judges every recorded transition TRUE, FALSE or NA (outside its scope). ' +
      D.rules.length + " concepts when sealed: " + alive + " alive, " + (D.rules.length - alive) + " withdrawn, " + nv + " versions in all.</p>" +
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
      '<p class="lede">The learned rules are written as definitions in <code>stepRules</code>. The Lean kernel (<code>decide +kernel</code>) checks two theorems. <em>consistent</em>: every rule holds on every recorded transition; <em>faithful</em>: Lean replays the winning run. The replay starts at level 0 and computes each step with the rules, and every step must equal the recording.</p>' +
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
          var lsl = [["revised", r.ls.revised], ["registered", r.ls.registered], ["withdrawn", r.ls.retired]].filter(function (x) { return x[1] && x[1].length; });
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
  var HOME_ANCHORS = ["home", "games", "compare", "data", "results", "repro", "faq", "bibtex", "autorepair-link"];
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
    if (head === "autorepair") { current = "autorepair"; autorepair(); return; }
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
        else if (view === "explain" || view === "notes" || view === "merge") { overview(D); scrollTo(head + "." + view); }
        else overview(D);
      }).catch(function (e) { app.innerHTML = "<p>" + esc(e.message) + "</p>"; });
      return;
    }
    var anchor = HOME_ANCHORS.indexOf(head) >= 0 ? head : "home";
    if (current === "home") { setNav(anchor === "games" || anchor === "compare" ? "games" : anchor === "data" ? "data" : "home"); scrollTo(anchor === "home" ? "" : anchor); return; }
    current = "home";
    home(anchor);
  }
  window.addEventListener("hashchange", route);
  route();
})();

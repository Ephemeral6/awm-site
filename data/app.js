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
  // English when there is a translation; otherwise the Chinese record stays folded under a label, never shown bare
  var CJK = /[㐀-鿿]/;
  var ZH_LABEL = "Agent's notes (original, in Chinese)";
  function zhFold(html) {
    return '<details class="orig"><summary>' + ZH_LABEL + '</summary><div>' + html + "</div></details>";
  }
  function preBi(en, zh) {
    if (en && !CJK.test(en)) return "<pre>" + esc(en) + "</pre>" + orig(zh, en);
    var src = zh || en;
    return src ? zhFold("<pre>" + esc(src) + "</pre>") : "";
  }
  function zhBi(en, zh) {
    if (en && !CJK.test(en)) return esc(en) + orig(zh, en);
    var src = zh || en;
    return src ? zhFold(esc(src)) : "";
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
  function typeset() {}                         // formulas are rendered to SVG by build.py (tools/tex2svg.js); nothing to do at runtime
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
      "<b>" + g + "</b> · " + i.levels + " levels · " + i.certified_actions.toLocaleString("en-US") + " certified actions · " + i.concepts + " concepts · score " + esc(i.score) +
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
        esc((i.axioms || []).join(", ") || "—"), "<code>" + esc(String(i.lean_sha || "—")) + "</code>",
        i.raw && i.raw.zip ? '<a href="' + esc(i.raw.zip) + '">' + esc(i.g) + ".zip</a>" : "—"];
    });
    return '<section id="repro"><h2>Reproducibility</h2>' +
      "<p>The paper's statement is in its <a href=\"#paper.Reproducibility-statement\">Reproducibility statement</a>: one command per game regenerates the model, tests and Lean project; the per-game Lean projects are checked with Lean 4.34.0. " +
      "Below, the sealed <code>Game.lean</code> of each game shown on this site, the local kernel check recorded in its <code>VERIFY.json</code>, and its sha256. Check it with <code>python ledger/lean_check.py &lt;formal directory&gt;</code> in the bench repository.</p>" +
      table(["Game", "Kernel check", "Axioms", "Game.lean sha256", "Raw files"], rows) + "</section>";
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
      '<a href="#repro">Reproducibility</a><a href="#faq">Questions</a><a href="#bibtex">BibTeX</a>';
    var T = S.tables || {};
    var results = '<section id="results"><h2>Main result: proving impossibility</h2>' +
      "<p>Two levels of <code>sc25</code> are sealed one unit below their minimum winning cost. The question is whether any legal winning sequence remains (§4 of the paper).</p>" +
      '<figure class="paper-figure"><img src="' + esc((S.figs || {}).l4) + '" alt="GPT-6 Astra claims a minimum cost of 22 on sealed sc25 level 4; AWM proves 19 in Lean." loading="lazy">' +
      '<figcaption class="paper-caption">Figure 4 of the paper. <a href="#paper.fig-l4attempts">Read its caption in the paper</a>.</figcaption></figure>' +
      ((S.p2 || {})["cert-l4"] ? '<div class="btns"><a class="btn primary" href="#cert">Inspect the certificate</a>' +
        ((S.p2 || {})["repair-l4"] || (S.p2 || {})["repair-l5"] ? '<a class="btn" href="#repair.' + ((S.p2 || {})["repair-l4"] ? "l4" : "l5") + '">Watch the repair</a>' : "") +
        '<span class="note">from a new AWM run, not one of the six runs in Table 3</span></div>' : "") +
      capWidget() + (T["tab:verdicts"] || "") +
      '<p class="note">More: <a href="#faq">questions about the proofs</a>, the <a href="#sc25">sc25 game</a> as played, and how <a href="#lp85.merge">eleven lp85 concepts became one rule</a> (§2.5).</p></section>';
    var cards = S.games.map(function (i) {
      return '<a class="gcard" href="#' + i.g + '"><img src="thumbs/' + i.g + '.png" alt="' + i.g + ', first frame" loading="lazy">' +
        '<div class="t"><b>' + i.g + "</b><span>" + i.levels + " levels · " + i.certified_actions.toLocaleString("en-US") + " certified actions</span>" +
        "<span>" + i.concepts + " concepts · " + i.withdrawn + " withdrawn</span></div></a>";
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
      '<section id="games"><h2>Appendix: the 25 games</h2><p>Every public ARC-AGI-3 game, as the agent played it. Each game has the same five views: overview with the agent\'s own explanation, step-by-step replay, concept book, Lean proof, and its raw files.</p>' +
      "<p class=\"note\">AWM's certified clears follow uncertified sessions of the same run in 22 games (Table 15 of the supplementary material).</p>" +
      '<div class="gallery">' + cards + "</div>" +
      '<h3 id="compare">Official results on the same 25 games</h3><p>' + (S.scores_note || "") + ":</p>" +
      ((S.tables || {})["tab:scores"] || (S.scores ? table(S.scores.head.map(esc), S.scores.rows.map(function (r) { return r.map(esc); }), [2, 3, 4, 5]) : "")) +
      "<p>Per game, from the supplementary material (" + esc(C.label) + "):</p>" +
      table(C.head.map(esc), crow, [1, 2, 3, 4, 5, 6, 7]) + "</section>" +
      '<section id="data"><h2>Data and sources</h2><p>Table 2 of the paper:</p>' + ((S.tables || {})["tab:lean"] || "") +
      "<p>All figures on this site are those reported in the paper and its supplementary material (benchmark commit <code>" + esc((S.data || {}).commit) + "</code>).</p>" +
      table(["What", "From"], [
        ["Per-game figures", "the supplementary material: Table 2 (Appendix A) and Tables 14–15 (Appendix E)"],
        ["Frames of every step", "<code>bench/runs/&lt;run&gt;/transitions.jsonl</code>; each frame pair is checked against the sealed <code>formal/abstract.jsonl</code> by tid = sha1(action, frame, next frame)"],
        ["Reasoning at each step", "<code>bench/runs/&lt;run&gt;/reasoning.jsonl</code>, sent with each action"],
        ["Bets and journal lines", "the timeline of <code>bench/archive/&lt;seal&gt;/report/index.html</code>, generated from the journal"],
        ["The agent's explanation", "<code>bench/archive/&lt;seal&gt;/formal/…/explain.md</code>; the repaired-rule notes come from the header of <code>Game.lean</code>"],
        ["Concept book and its history", "<code>bench/ledger/games/&lt;game&gt;/registry.json</code> and <code>concepts/*.py</code>, the books the paper counts"],
        ["Lean proof shown on each game's page", "the sealed run's <code>formal/Game.lean</code> and <code>formal/VERIFY.json</code>"],
        ["Official replays", "<code>MANIFEST.json</code>, <code>bench/ledger/games/&lt;game&gt;/analysis/official.json</code>"],
        ["How to play", "<code>bench/site/data/playguide.json</code> and its rule-checked revision"],
        ["Official results", "<code>bench/site/data/official_public_demo.json</code>"],
        ["Paper", "<code>paper-revision/main.tex</code>, the <code>sec/*.tex</code> it inputs, <code>Reference.bib</code>, figures (git " + esc(P.source_commit || "—") + ")"],
        ["Colour palette", "<code>" + esc(S.palette_src) + "</code>"]
      ]) + "</section>" + repro() + faq() +
      bibtex() +
      '<footer class="site">' + provenance() + ".</footer></article></div>";
    addExploreCards(document.getElementById("paper"));
    p2Links(document.getElementById("paper"));
    typeset(document.getElementById("paper"));
    heroAnim(); capInit(); bibInit();
    scrollTo(anchor && anchor !== "home" ? anchor : "");
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

  // ---------------------------------------------------------------- P2: certificate browser, repair replay, unseen states
  var P2 = S.p2 || {};
  function loadP2(name) { return load("data/p2-" + name + ".js").then(function () { return (window.AWM_P2 || {})[name]; }); }
  function paintGrid(cv, g, pal, scale) {
    // g: {w, h, x} with x = w*h hex digits (colour indices), or a path to an image under p2/
    var ctx = cv.getContext("2d");
    if (typeof g === "string") {
      var im = new Image(); im.onload = function () { cv.width = im.width; cv.height = im.height; ctx.drawImage(im, 0, 0); }; im.src = "p2/" + g; return;
    }
    var P = pal.map(function (h) { return [parseInt(h.substr(1, 2), 16), parseInt(h.substr(3, 2), 16), parseInt(h.substr(5, 2), 16)]; });
    var a = new Uint8Array(g.w * g.h);
    for (var i = 0; i < a.length; i++) a[i] = parseInt(g.x.charAt(i), 16);
    drawFrame(cv, { w: g.w, h: g.h, a: a }, P, scale || 4, null, null);
  }
  function p2Head(title, sec, src) {
    return '<p class="crumb"><a href="#home">Paper</a> / <a href="#results">Main result</a> / ' + esc(title) + "</p><h1>" + esc(title) + "</h1>" +
      '<p class="note">Paper ' + esc(sec) + ". " + src + "</p>";
  }
  function newRunNote(D) {
    return "Data: a new AWM run, <code>" + esc(D.run) + "</code> (" + esc(D.batch || "") + "), not one of the six runs in Table 3 of the paper. Source: <code>" + esc(D.source) + "</code>.";
  }

  function certView(arg) {
    setNav("home");
    app.innerHTML = '<p class="muted">Loading the certificate…</p>';
    loadP2("cert-l4").then(function (D) {
      var V = {}, out = {};
      D.states.forEach(function (s) { V[s.id] = s.V; });
      D.edges.forEach(function (e) { (out[e.from] = out[e.from] || []).push(e); });
      var head = ["state"].concat(D.fields).concat(["Φ"]);
      app.innerHTML = p2Head("Certificate browser: sealed sc25 level 4", "§2.4 and §4.2", newRunNote(D)) +
        '<p class="lede">A potential Φ on every state of the run\'s model. Lean checks Φ(w) ≤ cost(w, a) + Φ(w′) on every legal transition and Φ(w) ≤ cost on every winning move, so every winning sequence from the start costs at least Φ(start).</p>' +
        '<div class="pane"><h4>Main theorem (as written by the run)</h4><pre><code>' + esc(D.theorem) + "</code></pre>" +
        "<h4>#print axioms, re-checked on this machine</h4><pre><code>" + esc(D.axioms) + "</code></pre>" +
        '<p><a class="btn" href="p2/' + esc(D.lean_url) + '" download>Download Level4Cert.lean</a></p>' +
        '<p class="note">Φ(start) = <b>' + esc(D.bound) + "</b> in the run's units, which charge the winning move (budget " + esc(D.budget) +
        "). Under the engine's accounting this is 19, the engine optimum; the paper counts such a bound as correct (§4.2). " +
        "States from which the model cannot win carry Φ ≥ 200. The states are those of the run's macro abstraction of its own level-4 model; that this abstraction is looser than the run's model is the agent's argument, not a Lean theorem.</p></div>" +
        '<div class="ctrl"><input type="search" id="cq" placeholder="Filter: a state number, or a field value such as row=25" style="flex:1;min-width:200px;padding:5px 8px;border:1px solid var(--line);border-radius:4px;background:var(--panel);color:var(--ink)">' +
        '<span class="note" id="cn"></span></div><div class="tbox"><table class="t" id="ct"></table></div><div class="btns"><button class="btn" type="button" id="cmore">Show more</button></div>';
      var limit = 60, rows = D.states;
      function match(s, q) {
        if (!q) return true;
        return q.split(/\s+/).every(function (t) {
          var m = /^([a-z ]+?)\s*=\s*(\S+)$/i.exec(t.replace(/_/g, " "));
          if (m) { var v = s.w[m[1].trim()]; return v !== undefined && String(v) === m[2]; }
          return String(s.id) === t || String(s.V) === t;
        });
      }
      function render() {
        var q = document.getElementById("cq").value.trim();
        var hits = rows.filter(function (s) { return match(s, q); });
        hits.sort(function (a, b) { return (b.id === D.start) - (a.id === D.start); });
        document.getElementById("cn").textContent = hits.length + " of " + rows.length + " states";
        document.getElementById("ct").innerHTML = "<thead><tr>" + head.map(function (h) { return "<th>" + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
          hits.slice(0, limit).map(function (s) {
            return '<tr class="crow' + (s.id === D.start ? " start" : "") + '" data-id="' + s.id + '"><td class="n">' + s.id + (s.id === D.start ? ' <span class="chip con">start</span>' : "") + "</td>" +
              D.fields.map(function (f) { return "<td>" + esc(s.w[f]) + "</td>"; }).join("") + '<td class="n"><b>' + s.V + "</b></td></tr>";
          }).join("") + "</tbody>";
        document.getElementById("cmore").style.display = hits.length > limit ? "" : "none";
      }
      function expand(tr) {
        var nx = tr.nextElementSibling;
        if (nx && nx.classList.contains("cdet")) { nx.remove(); return; }
        var id = parseInt(tr.getAttribute("data-id"), 10);
        var lines = (out[id] || []).map(function (e) {
          var rhs = e.cost + (e.to === "WIN" ? 0 : V[e.to]);
          var ok = V[id] <= rhs;
          return "<tr><td>" + esc(e.a) + "</td><td>" + (e.to === "WIN" ? "win" : '<a href="#cert.' + e.to + '">' + e.to + "</a>") + '</td><td class="n">' + e.cost +
            '</td><td class="n">' + (e.to === "WIN" ? "—" : V[e.to]) + '</td><td class="mono">' + V[id] + " ≤ " + e.cost + (e.to === "WIN" ? "" : " + " + V[e.to]) + " = " + rhs +
            '</td><td><span class="chip ' + (ok ? "ok" : "bad") + '">' + (ok ? "✓" : "✗") + "</span></td></tr>";
        }).join("");
        var row = document.createElement("tr"); row.className = "cdet";
        row.innerHTML = '<td colspan="' + head.length + '"><table class="t"><thead><tr><th>Action</th><th>To</th><th>Cost</th><th>Φ(w′)</th><th>Φ(w) ≤ cost + Φ(w′)</th><th></th></tr></thead><tbody>' + lines + "</tbody></table></td>";
        tr.parentNode.insertBefore(row, tr.nextSibling);
      }
      document.getElementById("cq").oninput = function () { limit = 60; render(); };
      document.getElementById("cmore").onclick = function () { limit += 120; render(); };
      document.getElementById("ct").onclick = function (e) { var tr = e.target.closest("tr.crow"); if (tr && !e.target.closest("a")) expand(tr); };
      if (arg) document.getElementById("cq").value = arg;
      render();
      var first = document.querySelector("#ct tr.crow"); if (first) expand(first);
      window.scrollTo(0, 0);
    }).catch(function (e) { app.innerHTML = "<p>" + esc(e.message) + "</p>"; });
  }

  function repairView(lv) {
    setNav("home");
    var name = "repair-" + lv;
    if (!P2[name]) { app.innerHTML = p2Head("Repair replay, level " + lv.slice(1), "§4.3", "") + "<p>This replay is not available yet.</p>"; return; }
    loadP2(name).then(function (D) {
      var i = 0, N = D.steps.length;
      var maxB = Math.max.apply(null, D.bounds.map(function (b) { return b.value; }));
      app.innerHTML = p2Head("Repair replay: sealed sc25 level " + lv.slice(1), "§4.3", newRunNote(D)) +
        '<div class="btns">' + ["l4", "l5"].filter(function (x) { return P2["repair-" + x]; }).map(function (x) {
          return '<a class="btn' + (x === lv ? " primary" : "") + '" href="#repair.' + x + '">Level ' + x.slice(1) + "</a>"; }).join("") + "</div>" +
        '<div class="pane"><h4>The only feedback the run received</h4><p class="bet">' + esc(D.signal) + "</p></div>" +
        '<div class="rp"><div><div class="cv"><canvas id="rf"></canvas></div><div class="ctrl"><button id="rp">◀</button><span class="mono" id="ri"></span><button id="rn">▶</button>' +
        '<input type="range" id="rs" min="0" max="' + (N - 1) + '" value="0" aria-label="Position"></div>' +
        '<div class="ctrl">' + D.steps.map(function (s, j) { return s.caption ? '<button class="rjump" data-j="' + j + '">' + esc(s.title.split(" · ")[0]) + (/^After/.test(s.caption) ? " end" : " start") + "</button>" : ""; }).join("") + "</div></div>" +
        '<div><div class="pane"><h4 id="rh"></h4><p id="rc" class="claim"></p></div>' +
        '<div class="pane"><h4>Bound</h4>' + D.bounds.map(function (b) {
          return '<div style="margin:6px 0"><div class="note">' + esc(b.label) + (b.note ? " · " + esc(b.note) : "") + '</div><div style="display:flex;align-items:center;gap:8px"><div style="height:14px;background:var(--accent);border-radius:2px;width:' +
            (100 * b.value / maxB).toFixed(1) + '%"></div><b>' + esc(b.value) + "</b></div></div>"; }).join("") + "</div></div></div>" +
        "<h2>The rule before and after</h2>" + (D.rule_diff.file ? '<p class="note"><code>' + esc(D.rule_diff.file) + "</code>" + (D.rule_diff.why ? " · " + esc(D.rule_diff.why) : "") + "</p>" : "") + "<div class=\"rp\"><div><h4>Before</h4><pre><code>" + esc(D.rule_diff.before) + "</code></pre></div><div><h4>After</h4><pre><code>" + esc(D.rule_diff.after) + "</code></pre></div></div>";
      function show(k) {
        i = (k + N) % N;
        var s = D.steps[i];
        paintGrid(document.getElementById("rf"), s.frame, D.palette, 8);
        document.getElementById("ri").textContent = (i + 1) + " / " + N;
        document.getElementById("rh").textContent = s.title || ("Step " + (i + 1));
        document.getElementById("rc").textContent = s.caption || "";
        document.getElementById("rs").value = i;
      }
      document.getElementById("rp").onclick = function () { show(i - 1); };
      document.getElementById("rn").onclick = function () { show(i + 1); };
      document.getElementById("rs").oninput = function () { show(parseInt(this.value, 10)); };
      Array.prototype.forEach.call(app.querySelectorAll(".rjump"), function (b) { b.onclick = function () { show(parseInt(b.getAttribute("data-j"), 10)); }; });
      show(0);
      window.scrollTo(0, 0);
    }).catch(function (e) { app.innerHTML = "<p>" + esc(e.message) + "</p>"; });
  }

  function unseenView(game) {
    setNav("home");
    var name = "unseen-" + game;
    app.innerHTML = '<p class="muted">Loading…</p>';
    loadP2(name).then(function (D) {
      var sets = Object.keys(D.sets), cur = sets[0], idx = 0, rnd = 1;
      var labels = { trajectories: "New trajectories", layouts: "New layouts", changed_mechanic: "Changed hidden mechanic" };
      app.innerHTML = p2Head("Unseen states: " + game, "§3, “Generalization beyond observed transitions”",
          "Data: transitions from random play (local engine, seeds 0–9) whose previous screen never occurs in the recorded runs, drawn " + D.sets[cur].length + " per set from the test sets behind the paper's readings (<code>" + esc(D.source) + "</code>). The rules are frozen at the end of play.") +
        '<div class="btns">' + ["lp85", "ft09"].filter(function (g) { return P2["unseen-" + g]; }).map(function (g) {
          return '<a class="btn' + (g === game ? " primary" : "") + '" href="#unseen.' + g + '">' + g + "</a>"; }).join("") + "</div>" +
        '<div class="ctrl">' + sets.map(function (s) { return '<label><input type="radio" name="uset" value="' + s + '"' + (s === cur ? " checked" : "") + "> " + esc(labels[s] || s) + "</label>"; }).join(" ") +
        ' <button class="btn" type="button" id="udraw">Draw another transition</button></div>' +
        '<p class="note" id="unote"></p>' +
        '<div class="boards" style="display:grid;grid-template-columns:repeat(' + (game === "lp85" ? 3 : 2) + ',minmax(0,1fr));gap:10px">' +
        '<figure style="margin:0"><figcaption class="note">Before (action circled)</figcaption><div class="cv"><canvas id="ub"></canvas></div></figure>' +
        (game === "lp85" ? '<figure style="margin:0"><figcaption class="note">Predicted by the frozen rule (tiles only)</figcaption><div class="cv"><canvas id="up"></canvas></div></figure>' : "") +
        '<figure style="margin:0"><figcaption class="note">Actual next frame</figcaption><div class="cv"><canvas id="ua"></canvas></div></figure></div>' +
        '<div class="pane" style="margin-top:12px"><dl class="kv" id="ukv"></dl></div>';
      function grid2(g) { var a = new Uint8Array(g.w * g.h); for (var i = 0; i < a.length; i++) a[i] = parseInt(g.x.charAt(i), 16); return { w: g.w, h: g.h, a: a }; }
      var PAL = D.palette.map(function (h) { return [parseInt(h.substr(1, 2), 16), parseInt(h.substr(3, 2), 16), parseInt(h.substr(5, 2), 16)]; });
      function show() {
        var r = D.sets[cur][idx];
        var m = /^ACTION6:(\d+),(\d+)/.exec(r.action || "");
        drawFrame(document.getElementById("ub"), grid2(r.before), PAL, 6, null, m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : null);
        drawFrame(document.getElementById("ua"), grid2(r.after), PAL, 6, null, null);
        if (game === "lp85") { var pc = document.getElementById("up"); if (r.predicted) drawFrame(pc, grid2(r.predicted), PAL, 6, null, null); else { pc.width = pc.height = 0; } }
        document.getElementById("ukv").innerHTML = "<dt>Transition</dt><dd><code>" + esc(r.tid) + "</code> · seed " + esc(r.seed) + " · level " + esc(r.level) + "</dd>" +
          "<dt>Action</dt><dd><code>" + esc(r.action) + "</code></dd><dt>Cells changed</dt><dd>" + esc(r.changed_cells) + "</dd>" +
          '<dt>Frozen rules</dt><dd><span class="chip ' + (r.verdict === "TRUE" ? "ok" : r.verdict === "FALSE" ? "bad" : "") + '">' + esc(r.verdict) + "</span> " +
          (r.verdict === "TRUE" ? "accept the transition" : r.verdict === "FALSE" ? "report a contradiction" : "stay silent") + "</dd>" +
          (r.prediction ? '<dt>Prediction</dt><dd><span class="chip ' + (r.prediction === "right" ? "ok" : "bad") + '">' + esc(r.prediction) + "</span> tile layout " + (r.prediction === "right" ? "equals" : "differs from") + " the actual one</dd>" : "");
        document.getElementById("unote").textContent = cur === "changed_mechanic" ?
          "The hidden click pattern of ft09 is changed: each click now changes 110 or 146 cells instead of 38 (§3). The frozen rules report a contradiction on every such transition." : "";
      }
      Array.prototype.forEach.call(document.querySelectorAll('input[name="uset"]'), function (el) { el.onchange = function () { cur = el.value; idx = 0; show(); }; });
      document.getElementById("udraw").onclick = function () { rnd = (rnd * 1103515245 + 12345) % 2147483648; idx = rnd % D.sets[cur].length; show(); };
      show();
      window.scrollTo(0, 0);
    }).catch(function (e) { app.innerHTML = "<p>" + esc(e.message) + "</p>"; });
  }
  function p2Links(root) {
    // entry points, only for the parts whose data exist
    function after(test, html) {
      var ps = root.querySelectorAll("p");
      for (var i = 0; i < ps.length; i++) if (test(ps[i].textContent)) { var d = document.createElement("p"); d.className = "note"; d.innerHTML = html; ps[i].parentNode.insertBefore(d, ps[i].nextSibling); return; }
    }
    if (P2["repair-l4"] || P2["repair-l5"])
      after(function (t) { return /Both repairs succeed within four additional attempts/.test(t); },
        '<a href="#repair.' + (P2["repair-l4"] ? "l4" : "l5") + '">Watch the repair</a> (a new run, not one of Table 3).');
    if (P2["unseen-lp85"] || P2["unseen-ft09"])
      after(function (t) { return /frozen rules reject every resulting transition/.test(t); },
        '<a href="#unseen.' + (P2["unseen-lp85"] ? "lp85" : "ft09") + '">Try it</a>: draw transitions from the test sets.');
  }

  // ---------------------------------------------------------------- one game: shared parts
  function gameNav(g, active) {
    var items = [["", "Overview"], ["replay", "Replay"], ["rules", "Concept book"], ["proof", "Lean proof"], ["raw", "Raw files"]];
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
    var g = D.g;
    var ment = paperMentions(g);
    app.innerHTML = crumb(g) +
      '<h1 style="font-family:var(--mono);font-size:34px">' + g + "</h1>" +
      '<p class="lede">ARC-AGI-3 public game <code>' + esc(D.game) + "</code>, run <code>" + esc(D.run) + "</code>, sealed as <code>" + esc(D.seal) + "</code>.</p>" +
      gameNav(g, "") +
      (ment.length ? "<p>In the paper: " + ment.map(function (s) { return '<a href="#' + secId(s) + '">' + esc((s.number ? "§" + s.number + " " : "") + s.title) + "</a>"; }).join(", ") + "</p>" : "") +
      '<div class="rp"><div><h2 style="margin-top:8px">How to play</h2><div class="prose md">' + zhBi(D.playguide.en, D.playguide.zh) + "</div></div>" +
      '<div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">' +
      '<figure style="margin:0"><figcaption class="note">Before the first recorded step</figcaption><img src="thumbs/' + g + '.png" alt="first frame" style="width:100%;image-rendering:pixelated;border-radius:3px"></figure>' +
      '<figure style="margin:0"><figcaption class="note">After the last recorded step</figcaption><img src="thumbs/' + g + '-last.png" alt="last frame" style="width:100%;image-rendering:pixelated;border-radius:3px"></figure>' +
      '</div><p><a class="btn primary" href="#' + g + '.replay">Open the replay</a></p></div></div>' +
      "<h2>Reported in the paper</h2><p class=\"note\">From the supplementary material: Table 2 (Appendix A) and Tables 14–15 (Appendix E).</p>" +
      table(["", ""], D.stats.map(function (r) { return [esc(r[0]), esc(r[1])]; })) +
      "<h3>Official scores on this game (systems of Table 13 of the supplementary material)</h3>" + table(["System", "Official score"], D.official.map(function (r) { return [esc(r[0]), esc(Number(r[1]).toFixed(1))]; }), [1]) +
      (D.replays.length ? "<h3>Official replays</h3><p>" + D.replays.map(function (r) {
        return '<a href="' + esc(r.url) + '" target="_blank" rel="noopener">arcprize.org replay ' + esc(r.url.split("/").pop().slice(0, 8)) + "… ↗</a>" + (r.cert ? ' <span class="chip ok">certified</span>' : "");
      }).join("<br>") + "</p>" : "") +
      '<h2 id="' + g + '.explain">The agent\'s explanation</h2><p class="note">Written by the agent when it sealed the run (<code>explain.md</code>).</p>' +
      (D.explain.en && !CJK.test(D.explain.en)
        ? '<div class="md prose">' + D.explain.en + "</div>" +
          (D.explain.zh ? '<details class="orig"><summary>Original</summary><div class="md" style="white-space:normal">' + D.explain.zh + "</div></details>" : "")
        : (D.explain.zh ? '<p class="note">No English translation yet.</p>' + zhFold('<div class="md" style="white-space:normal">' + D.explain.zh + "</div>") : "<p>—</p>")) +
      (D.notes.en ? '<h2 id="' + g + '.notes">Notes on the repaired rules (header of Game.lean)</h2>' + preBi(D.notes.en, D.notes.zh) : "") +
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
        var at = v.run === D.run ? '<a href="#' + g + ".replay.s" + v.st + '">step ' + v.st + "</a>" : "step " + v.st + " of run <code>" + esc(v.run || "—") + "</code>";
        return '<div class="v"><div class="h">v' + v.v + " · " + at + " · " + esc(v.at || "") + "</div>" +
          '<div class="claim">' + zhBi(v.doc, v.doc_zh) + "</div>" +
          (v.scope ? '<div class="note"><b>Scope:</b> ' + zhBi(v.scope, v.scope_zh) + "</div>" : "") +
          (v.note ? '<div class="note"><b>Added in this version:</b> ' + zhBi(v.note, v.note_zh) + "</div>" : "") + "</div>";
      }).join("");
      return '<details class="item" id="' + g + ".rules." + tok(r.name) + '"><summary><span class="name">' + esc(r.name) + "</span> " + chips +
        '<div class="claim">' + (CJK.test(last.doc || "") ? '<span class="muted">(original in Chinese)</span>' : esc(last.doc || "")) + '</div></summary><div class="body"><div class="vers">' + vs + "</div>" +
        (r.src ? '<details class="item"><summary>Source as sealed (Python, as written)</summary><div class="body"><pre><code>' + esc(r.src) + "</code></pre></div></details>" : "") +
        "</div></details>";
    }).join("");
    app.innerHTML = crumb(g, "Concept book") + "<h1>" + g + " · concept book</h1>" +
      '<p class="lede">Every concept the agent wrote while playing. Each is a Python hypothesis that judges every recorded transition TRUE, FALSE or NA (outside its scope). ' +
      D.rules.length + " concepts written, " + (D.rules.length - alive) + " withdrawn (Appendix A of the supplementary material).</p>" +
      '<p class="note">This is the book in <code>bench/ledger/games/' + esc(g) + "/registry.json</code>, the one the paper counts. A version written in the run shown on the Replay tab links to its step.</p>" +
      gameNav(g, "rules") +
      '<div class="btns"><button class="btn" type="button" id="xall">Expand all</button><button class="btn" type="button" id="call">Collapse all</button></div>' + items +
      (D.lib ? '<details class="item"><summary>Shared vocabulary <code>_lib.py</code> (as written)</summary><div class="body"><pre><code>' + esc(D.lib) + "</code></pre></div></details>" : "") +
      sources([D.src[0], D.src[2]]);
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
      gameNav(g, "proof") +
      "<h2>Reported in the paper</h2><p class=\"note\">Table 2 of the supplementary material (Appendix A), counted over the game's Lean project in <code>bench/ledger/games/" + esc(g) + "/lean2/</code> (in this game's Raw files).</p>" +
      table(["", ""], (P.paper || []).map(function (r) { return [esc(r[0]), esc(r[1])]; })) +
      "<h2>The sealed run's Game.lean</h2>" + table(["", ""], P.rows.map(function (r) { return [esc(r[0]), r[0].indexOf("sha256") >= 0 ? "<code>" + esc(r[1]) + "</code>" : esc(r[1])]; })) +
      "<h2>Rules (" + P.names.length + ")</h2><p>" + P.names.map(function (n) {
        return known[n] ? '<a class="chip con" href="#' + g + ".rules." + tok(n) + '">' + esc(n) + "</a>" : '<span class="chip">' + esc(n) + "</span>";
      }).join("") + "</p>" +
      "<h2>Theorems</h2><p>" + P.thms.map(function (t) { return "<code>" + esc(t) + "</code> "; }).join("") + "</p>" +
      (D.notes.en ? "<h2>Notes in the file header</h2>" + preBi(D.notes.en, D.notes.zh) : "") +
      "<h2>Game.lean (source as written; generated data section omitted)</h2><pre><code>" + esc(P.view) + "</code></pre>" + sources([P.path]);
    window.scrollTo(0, 0);
  }

  // ---------------------------------------------------------------- raw files (unedited, for reproduction)
  function rawFiles(D) {
    var g = D.g, R = D.raw || {};
    app.innerHTML = crumb(g, "Raw files") + "<h1>" + g + " · raw files</h1>" +
      '<p class="lede">Unedited files from the run, provided for reproduction (supplementary material).</p>' + gameNav(g, "raw") +
      (R.zip ? '<p><a class="btn primary" href="' + esc(R.zip) + '" download>Download ' + esc(g) + ".zip</a></p>" : "") +
      table(["File (path in the bench repository)"], (R.files || []).map(function (f) { return ["<code>" + esc(f[0]) + "</code>"]; })) +
      ((R.skipped || []).length ? "<p class=\"note\">Left out because they contain a local path or a name: " +
        R.skipped.map(function (f) { return "<code>" + esc(f[0]) + "</code>"; }).join(", ") + ".</p>" : "");
    window.scrollTo(0, 0);
  }

  // ---------------------------------------------------------------- replay
  var RP = null;
  function replay(D, arg) {
    var g = D.g, R = D.replay, N = R.recs.length, SC = 8;
    app.innerHTML = crumb(g, "Replay") + "<h1>" + g + " · replay</h1>" +
      '<p class="lede">The recorded transitions of run <code>' + esc(D.run) + "</code>. Left: the frame before the action (a click is circled). Right: the frame after (changed cells are outlined). Beside them: what the agent was thinking at this step, and the bet and journal of its batch.</p>" +
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
        return '<li class="' + esc(l[0]) + '"><span class="tm">' + esc(l[1]) + '</span><span class="tg">' + esc(l[2]) + "</span> " + zhBi(l[3], l[4]) + "</li>";
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
        if (r.cl) w += '<ul class="note">' + Object.keys(r.cl).map(function (k) { return "<li><b>" + esc(k) + "</b>: " + zhBi(r.cl[k], (r.clz || {})[k]) + "</li>"; }).join("") + "</ul>";
        if (r.ls) {
          var lsl = [["revised", r.ls.revised], ["registered", r.ls.registered], ["withdrawn", r.ls.retired]].filter(function (x) { return x[1] && x[1].length; });
          w += '<details class="note"><summary>Last settle (after step ' + esc(r.ls.after_step) + "): " + esc(r.ls.concepts) + " concepts, " + esc(r.ls.counterexamples) + " counterexamples" +
            lsl.map(function (x) { return ", " + x[1].length + " " + x[0]; }).join("") + "</summary>" +
            lsl.map(function (x) { return "<ul>" + x[1].map(function (s) { return "<li>" + zhBi(s) + "</li>"; }).join("") + "</ul>"; }).join("") + "</details>";
        }
      } else {
        w += (r.pr ? "<p>Model prediction → hits: " + zhBi(r.pr) + "</p>" : "") + (r.sp && r.sp.length ? "<p>Concepts that spoke: " + r.sp.map(chip).join("") + "</p>" : "");
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
        (b.bet ? '<div class="bet"><b>Bet:</b> ' + zhBi(b.bet, b.bet_zh) + "</div>" : "") +
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
  var HOME_ANCHORS = ["home", "games", "compare", "data", "results", "repro", "faq", "bibtex"];
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
    if (head === "cert" && P2["cert-l4"]) { current = "cert"; certView(parts.slice(1).join(".")); return; }
    if (head === "repair") { current = "repair"; repairView(parts[1] || (P2["repair-l4"] ? "l4" : "l5")); return; }
    if (head === "unseen" && (P2["unseen-lp85"] || P2["unseen-ft09"])) { current = "unseen"; unseenView(parts[1] || (P2["unseen-lp85"] ? "lp85" : "ft09")); return; }
    if (head === "paper") {                     // a place inside the paper on the home page
      if (current !== "home") { current = "home"; home(""); }
      setNav("home");
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
        else if (view === "raw" || view === "wb") rawFiles(D);
        else if (view === "explain" || view === "notes" || view === "merge") { overview(D); scrollTo(head + "." + view); }
        else overview(D);
      }).catch(function (e) { app.innerHTML = "<p>" + esc(e.message) + "</p>"; });
      return;
    }
    if (h && HOME_ANCHORS.indexOf(head) < 0) {   // an address no view answers: say so instead of showing the home page
      current = "notfound"; setNav("");
      app.innerHTML = '<h1>Page not found</h1><p>No page answers <code>#' + esc(h) + '</code>.</p><p><a href="#home">Back to the home page</a></p>';
      window.scrollTo(0, 0);
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

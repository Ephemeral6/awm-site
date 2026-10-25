// AWM site v3, one game page: a single scrolling page (replay first), a sub-navigation that follows the scroll,
// and the replay of the certified run (data/replay-<game>.js, written by build.py, loaded with the page).
// Addresses of the v2 tabs (#how, #replay, #model, #proof, #files, #sealed, #model/<rule>) land on the same sections.
(function () {
  "use strict";
  var G = window.AWM_GAME;
  document.documentElement.classList.add("js");

  function toRule(rule) {
    var el = document.getElementById("rule-" + rule);
    if (!el) return;
    el.scrollIntoView({ block: "center", behavior: "smooth" });
    el.classList.add("hl"); setTimeout(function () { el.classList.remove("hl"); }, 1600);
  }
  function fromHash() {
    var h = decodeURIComponent(location.hash.slice(1)).split("/");
    if (h[0] === "model" && h[1]) toRule(h[1]);
  }
  window.addEventListener("hashchange", fromHash);
  fromHash();

  // sub-navigation: mark the section being read
  var links = Array.prototype.slice.call(document.querySelectorAll("[data-sec]"));
  // the current section is the last one whose top has passed below the sticky bars; at the bottom of the page, the last one
  var secs = links.map(function (a) { return document.getElementById(a.getAttribute("data-sec")); });
  var queued = false;
  function mark() {
    queued = false;
    var cur = 0;
    secs.forEach(function (s, i) { if (s && s.getBoundingClientRect().top <= 130) cur = i; });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) cur = secs.length - 1;
    links.forEach(function (a, i) { a.classList.toggle("on", i === cur); });
  }
  window.addEventListener("scroll", function () { if (!queued) { queued = true; requestAnimationFrame(mark); } }, { passive: true });
  mark();

  // ------------------------------------------------------------ replay
  var RP = null, loading = false;
  function load(src) {
    return new Promise(function (ok, bad) {
      var s = document.createElement("script");
      s.src = src; s.charset = "utf-8"; s.onload = ok; s.onerror = function () { bad(new Error("Could not load " + src)); };
      document.head.appendChild(s);
    });
  }
  function startReplay() {
    if (RP || loading) return;
    loading = true;
    document.getElementById("rp-act").textContent = "Loading…";
    load("../../data/replay-" + G + ".js").then(function () { RP = replay(window.AWM_REPLAY[G]); })
      .catch(function (e) { document.getElementById("rp-act").textContent = e.message; });
  }

  var ACT = { ACTION1: "↑ up", ACTION2: "↓ down", ACTION3: "← left", ACTION4: "→ right", ACTION5: "space", ACTION7: "undo", RESET: "reset" };
  function actName(a) {
    var m = /^ACTION6:(\d+),(\d+)/.exec(a);
    if (m) return "click (" + m[1] + ", " + m[2] + ")";
    return ACT[a.split(":")[0]] || a;
  }
  function hexFrame(o) { var a = new Uint8Array(o.w * o.h); for (var i = 0; i < a.length; i++) a[i] = parseInt(o.x.charAt(i), 16); return { w: o.w, h: o.h, a: a }; }
  function patch(b, d) { var a = b.a.slice(); for (var i = 0; i < d.length; i++) { var v = d[i]; a[v >> 4] = v & 15; } return { w: b.w, h: b.h, a: a }; }

  function replay(D) {
    var N = D.steps.length, pal = D.pal.map(function (h) { return [parseInt(h.substr(1, 2), 16), parseInt(h.substr(3, 2), 16), parseInt(h.substr(5, 2), 16)]; });
    // frames: B[i] = screen before step i, X[i] = screen after it
    var B = new Array(N), X = new Array(N), prev = hexFrame(D.f0);
    for (var i = 0; i < N; i++) {
      var s = D.steps[i];
      B[i] = s.p ? hexFrame(s.p) : prev;
      X[i] = Array.isArray(s.n) ? patch(B[i], s.n) : hexFrame(s.n);
      prev = X[i];
    }
    var desc = {};
    D.rules.forEach(function (r) { var el = document.querySelector("#rule-" + CSS.escape(r) + " > span"); desc[r] = el ? el.textContent : ""; });
    var cv = document.getElementById("rp-cv"), sl = document.getElementById("rp-slider");
    sl.max = N - 1;
    var cur = 0, timer = null, SC = 8;
    // level marks under the slider
    var lv = document.getElementById("rp-levels"), marks = "";
    for (var k = 0; k < N; k++) if (D.steps[k].L > D.steps[k].l) marks += '<i style="left:' + (100 * (k + 0.5) / N).toFixed(2) + '%" title="Level ' + D.steps[k].L + ' reached"></i>';
    lv.innerHTML = marks;

    function draw(f, before, click) {
      cv.width = f.w * SC; cv.height = f.h * SC;
      var ctx = cv.getContext("2d"), img = ctx.createImageData(f.w * SC, f.h * SC), d = img.data, W = f.w * SC;
      for (var y = 0; y < f.h; y++) for (var x = 0; x < f.w; x++) {
        var c = pal[f.a[y * f.w + x]] || [0, 0, 0];
        for (var yy = 0; yy < SC; yy++) { var o = ((y * SC + yy) * W + x * SC) * 4; for (var xx = 0; xx < SC; xx++) { d[o] = c[0]; d[o + 1] = c[1]; d[o + 2] = c[2]; d[o + 3] = 255; o += 4; } }
      }
      ctx.putImageData(img, 0, 0);
      if (before && before.w === f.w && before.h === f.h) {
        ctx.strokeStyle = "#f0c419"; ctx.lineWidth = 2;
        for (var q = 0; q < f.a.length; q++) if (f.a[q] !== before.a[q]) ctx.strokeRect((q % f.w) * SC + 1, Math.floor(q / f.w) * SC + 1, SC - 2, SC - 2);
      }
      if (click) [["#ffffff", 3], ["#e0303a", 1.5]].forEach(function (s) {
        ctx.strokeStyle = s[0]; ctx.lineWidth = s[1]; ctx.beginPath(); ctx.arc(click[0] * SC + SC / 2, click[1] * SC + SC / 2, SC * 1.6, 0, 7); ctx.stroke();
      });
    }
    function show(i) {
      cur = Math.max(0, Math.min(N - 1, i));
      var s = D.steps[cur], m = /^ACTION6:(\d+),(\d+)/.exec(s.a);
      draw(X[cur], B[cur], m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : null);
      sl.value = cur;
      document.getElementById("rp-step").textContent = "Step " + (cur + 1) + " / " + N;
      document.getElementById("rp-lv").textContent = s.L > s.l ? "Level " + (s.l + 1) + " cleared" : "Level " + (Math.min(s.l, s.L) + 1);
      document.getElementById("rp-act").textContent = actName(s.a);
      var rr = (s.r || []).map(function (k) { return D.rules[k]; }), box = document.getElementById("rp-rules");
      // mark the same rules in the rule list further down
      Array.prototype.forEach.call(document.querySelectorAll(".rules li.now"), function (li) { li.classList.remove("now"); });
      rr.forEach(function (r) { var li = document.getElementById("rule-" + r); if (li) li.classList.add("now"); });
      if (box) box.innerHTML = rr.length
        ? rr.map(function (r) { return '<a href="#model/' + encodeURIComponent(r) + '" title="' + esc(desc[r]) + '">' + esc(r) + "</a>"; }).join("") +
          '<div class="rp-desc">' + rr.map(function (r) { return esc(desc[r]); }).filter(Boolean).join("<br>") + "</div>"
        : '<span class="none">' + (/^RESET/.test(s.a) ? "Restart of the level." : "No rule is linked to this step in the agent's record.") + "</span>";
    }
    function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
    function stop() { if (timer) { clearInterval(timer); timer = null; } document.getElementById("rp-play").textContent = "Play"; }
    function play() {
      if (timer) { stop(); return; }
      if (cur >= N - 1) show(0);
      document.getElementById("rp-play").textContent = "Pause";
      timer = setInterval(function () { if (cur >= N - 1) { stop(); return; } show(cur + 1); }, 1000 / parseFloat(document.getElementById("rp-speed").value));
    }
    document.getElementById("rp-play").onclick = play;
    document.getElementById("rp-first").onclick = function () { stop(); show(0); };
    document.getElementById("rp-prev").onclick = function () { stop(); show(cur - 1); };
    document.getElementById("rp-next").onclick = function () { stop(); show(cur + 1); };
    document.getElementById("rp-last").onclick = function () { stop(); show(N - 1); };
    document.getElementById("rp-speed").onchange = function () { if (timer) { stop(); play(); } };
    sl.oninput = function () { stop(); show(parseInt(sl.value, 10)); };
    document.getElementById("rp-rules") && document.getElementById("rp-rules").addEventListener("click", function (e) {
      var a = e.target.closest("a");
      if (!a) return;
      e.preventDefault(); stop();
      history.replaceState(null, "", a.getAttribute("href"));
      toRule(decodeURIComponent(a.getAttribute("href").split("/")[1]));
    });
    function onScreen() { var r = cv.getBoundingClientRect(); return r.bottom > 60 && r.top < window.innerHeight - 60; }
    document.addEventListener("keydown", function (e) {
      if (!onScreen() || /INPUT|SELECT|TEXTAREA|BUTTON/.test(e.target.tagName)) return;
      if (e.key === "ArrowRight") { stop(); show(cur + 1); e.preventDefault(); }
      else if (e.key === "ArrowLeft") { stop(); show(cur - 1); e.preventDefault(); }
      else if (e.key === " ") { play(); e.preventDefault(); }
    });
    show(0);
    return { stop: stop };
  }
  startReplay();
})();

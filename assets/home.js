// AWM site v3, home page: the sealed sc25 level-4 demo in the first screen.
// Data (data/sealed-l4.js, written by build.py from tools/sealed_frames.py): the game's cheapest winning route replayed on the
// engine with a budget of 18 (it runs out one action before the goal) and of 19 (it wins). The demo plays 18, then 19, and loops.
(function () {
  "use strict";
  var box = document.getElementById("sd");
  if (!box) return;
  var cv = document.getElementById("sd-cv"), banner = document.getElementById("sd-banner");
  var fill = document.getElementById("sd-fill"), capMark = document.getElementById("sd-cap");
  var cOut = document.getElementById("sd-c"), bOut = document.getElementById("sd-b"), playBtn = document.getElementById("sd-play");
  var capBtns = Array.prototype.slice.call(box.querySelectorAll("[data-cap]"));
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var METER_MAX = 22, STEP_MS = 260, HOLD_MS = 2600;

  function load(src) {
    return new Promise(function (ok, bad) {
      var s = document.createElement("script");
      s.src = src; s.onload = ok; s.onerror = function () { bad(new Error("Could not load " + src)); };
      document.head.appendChild(s);
    });
  }
  function hexFrame(o) { var a = new Uint8Array(o.w * o.h); for (var i = 0; i < a.length; i++) a[i] = parseInt(o.x.charAt(i), 16); return { w: o.w, h: o.h, a: a }; }
  function patch(b, d) { var a = b.a.slice(); for (var i = 0; i < d.length; i++) { var v = d[i]; a[v >> 4] = v & 15; } return { w: b.w, h: b.h, a: a }; }

  load("data/sealed-l4.js").then(function () { start(window.AWM_SEALED); }).catch(function () { /* the poster image stays */ });

  function start(D) {
    var pal = D.pal.map(function (h) { return [parseInt(h.substr(1, 2), 16), parseInt(h.substr(3, 2), 16), parseInt(h.substr(5, 2), 16)]; });
    var runs = {};
    Object.keys(D.runs).forEach(function (cap) {
      var prev = null;
      runs[cap] = D.runs[cap].map(function (s) {
        var f = Array.isArray(s.n) ? patch(prev, s.n) : hexFrame(s.n);
        prev = f;
        return { a: s.a, c: s.c, s: s.s, f: f };
      });
    });
    var ctx = cv.getContext("2d"), img = ctx.createImageData(512, 512);
    box.classList.add("live");

    function draw(f) {
      var SC = 512 / f.w, d = img.data;
      for (var y = 0; y < 512; y++) for (var x = 0; x < 512; x++) {
        var c = pal[f.a[Math.floor(y / SC) * f.w + Math.floor(x / SC)]] || [0, 0, 0], o = (y * 512 + x) * 4;
        d[o] = c[0]; d[o + 1] = c[1]; d[o + 2] = c[2]; d[o + 3] = 255;
      }
      ctx.putImageData(img, 0, 0);
    }
    var cap = "18", k = 0, timer = null, paused = false;
    function setCap(c) {
      cap = c; k = 0;
      bOut.textContent = c;
      capMark.style.left = (100 * parseInt(c, 10) / METER_MAX) + "%";
      capBtns.forEach(function (b) {
        var on = b.getAttribute("data-cap") === c;
        b.classList.toggle("on", on); b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      box.classList.remove("lost", "won");
      banner.textContent = "";
      show(0);
    }
    function show(i) {
      var s = runs[cap][i];
      // after the winning action the engine has already opened the next level (and reset its counter): keep the last frame
      // of this level and its counter; the winning action itself is not charged
      var v = s.s === "win" && i > 0 ? runs[cap][i - 1] : s;
      draw(v.f);
      cOut.textContent = v.c;
      fill.style.width = Math.min(100, 100 * v.c / METER_MAX) + "%";
      fill.classList.toggle("over", v.c > parseInt(cap, 10));
      if (s.s === "lost") { box.classList.add("lost"); banner.textContent = "Out of budget: the level is lost"; }
      else if (s.s === "win") { box.classList.add("won"); banner.textContent = "The same route wins with a budget of 19"; }
    }
    // one chain of timeouts at a time: every stop() bumps gen, so a timeout from an older chain does nothing
    var gen = 0;
    function later(fn, ms) { var g = gen; timer = setTimeout(function () { if (g === gen) fn(); }, ms); }
    function tick() {
      var R = runs[cap];
      if (k < R.length - 1) { k++; show(k); later(tick, STEP_MS); return; }
      // end of a run: hold, then switch to the other budget
      later(function () { setCap(cap === "18" ? "19" : "18"); later(tick, 700); }, HOLD_MS);
    }
    function stop() { gen++; clearTimeout(timer); timer = null; }
    function play() { stop(); paused = false; playBtn.textContent = "Pause"; later(tick, 500); }
    function pause() { stop(); paused = true; playBtn.textContent = "Play"; }
    // the banner is announced only after the reader uses a control, not on every automatic loop
    function heard() { banner.setAttribute("aria-live", "polite"); }
    playBtn.onclick = function () { heard(); if (paused) { if (k >= runs[cap].length - 1) setCap(cap); play(); } else pause(); };
    capBtns.forEach(function (b) { b.onclick = function () { heard(); stop(); setCap(b.getAttribute("data-cap")); play(); }; });
    // play only while the demo is on screen
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (!e.isIntersecting) stop(); else if (!paused && !timer) later(tick, 400); });
      }).observe(box);
    }
    setCap("18");
    if (reduced) pause(); else play();
  }
})();

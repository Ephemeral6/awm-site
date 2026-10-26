// AWM site, home page: the two-act hero video (Königsberg -> AWM/sc25). Picks the light or dark variant to match
// the site's own theme (OS preference, or the manual light/dark switch in site.js), and leaves the poster image
// alone — no <source> is attached — when the reader has asked for reduced motion.
(function () {
  "use strict";
  var v = document.getElementById("hero-video");
  if (!v) return;
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) return;

  function theme() {
    var cur = document.documentElement.getAttribute("data-theme");
    if (cur) return cur;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  v.muted = true;
  function setSrc() {
    var dark = theme() === "dark";
    var base = "assets/video/hero" + (dark ? "-dark" : "");
    v.poster = base + "-poster.webp";
    // mp4/h264 first: webm/vp9 can fail at decode time (not just load time, where <source> fallback
    // actually works), silently leaving the video stuck on "playing" with no frames advancing.
    v.innerHTML =
      '<source src="' + base + '.mp4" type="video/mp4">' + '<source src="' + base + '.webm" type="video/webm">';
    v.load();
    v.addEventListener("loadedmetadata", function play() {
      v.removeEventListener("loadedmetadata", play);
      var p = v.play();
      if (p && p.catch) p.catch(function () {});
    });
  }
  v.setAttribute("autoplay", "");
  setSrc();
  var btn = document.getElementById("theme");
  if (btn) btn.addEventListener("click", function () { setTimeout(setSrc, 0); });
})();

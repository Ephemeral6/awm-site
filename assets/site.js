// AWM site v2, every page: light/dark switch (remembered in this browser only), BibTeX dialog and copy,
// and the v1 addresses (#sc25.replay …) sent on to the new pages.
(function () {
  "use strict";
  var KEY = "awm-theme";
  var b = document.getElementById("theme");
  if (b) b.addEventListener("click", function () {
    var cur = document.documentElement.getAttribute("data-theme");
    if (!cur) cur = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    var nx = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", nx);
    try { localStorage.setItem(KEY, nx); } catch (e) {}
  });

  function copy(text, done, sel) {
    function fallback() {
      var r = document.createRange(); r.selectNodeContents(sel);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); done("Selected; press Ctrl+C.");
    }
    try { navigator.clipboard.writeText(text).then(function () { done("Copied."); }, fallback); } catch (e) { fallback(); }
  }
  var dlg = document.getElementById("bib");
  Array.prototype.forEach.call(document.querySelectorAll("[data-bibtex]"), function (el) {
    el.addEventListener("click", function () {
      if (dlg && dlg.showModal) dlg.showModal();
      else { var t = document.getElementById("bib-inline"); if (t) t.scrollIntoView(); }
    });
  });
  if (dlg) {
    dlg.querySelector("[data-close]").addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
    dlg.querySelector("[data-copy]").addEventListener("click", function () {
      var pre = document.getElementById("bib-text");
      copy(pre.textContent, function (m) { document.getElementById("bib-ok").textContent = m; }, pre);
    });
  }
  var inl = document.querySelector("[data-copy-inline]");
  if (inl) inl.addEventListener("click", function () {
    var pre = document.getElementById("bib-inline");
    copy(pre.textContent, function (m) { inl.textContent = m === "Copied." ? "Copied" : "Copy BibTeX"; }, pre);
  });

  // reduced motion: show the still first frame instead of each looping clip
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (still) Array.prototype.forEach.call(document.querySelectorAll("img[data-still]"), function (im) {
    im.src = im.getAttribute("data-still");
  });
  // games wall: a card's clip is downloaded when the card is hovered or focused, not with the page
  Array.prototype.forEach.call(document.querySelectorAll(".card"), function (c) {
    var im = c.querySelector("img[data-anim]");
    if (!im || still) return;
    function go() { if (!im.getAttribute("src")) im.src = im.getAttribute("data-anim"); }
    c.addEventListener("mouseenter", go); c.addEventListener("focus", go);
  });

  // v1 links: #<game>[.replay|.rules|.proof|.raw…] and #games on the home page
  if (document.body.querySelector("main.home") && location.hash) {
    var h = decodeURIComponent(location.hash.slice(1)).split(".");
    var tab = { replay: "replay", rules: "model", proof: "proof", raw: "files", wb: "files" }[h[1]] || "";
    if (/^(?=.*\d)[a-z0-9]{4}$/.test(h[0])) location.replace("games/" + h[0] + "/" + (tab ? "#" + tab : ""));
    else if (h[0] === "games" || h[0] === "compare") location.replace("games/");
  }
})();

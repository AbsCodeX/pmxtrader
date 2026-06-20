/**
 * pmxtrader docs — navigation, homepage class, smooth anchors.
 */
(function () {
  var root = document.documentElement;
  var path = window.location.pathname.replace(/\/$/, "") || "/";
  var isHome =
    path === "" ||
    path === "/" ||
    path.endsWith("/pmxtrader") ||
    path.endsWith("/pmxtrader/index.html") ||
    document.querySelector(".pmx-doc-home");

  if (isHome) {
    document.body.classList.add("pmx-home");
  }

  var toggle = document.querySelector(".pmx-site-header__toggle");
  var nav = document.getElementById("pmx-site-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (event) {
      var id = anchor.getAttribute("href");
      if (!id || id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: root.matches("[data-reduced-motion]") ? "auto" : "smooth" });
      history.replaceState(null, "", id);
    });
  });
})();

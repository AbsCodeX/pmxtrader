/**
 * pmxtrader docs — mobile drawer + theme helpers
 */
(function () {
  var root = document.documentElement;
  var path = window.location.pathname.replace(/\/$/, "") || "/";
  var isHome =
    path === "" ||
    path === "/" ||
    path.endsWith("/pmxtrader") ||
    document.querySelector(".pmx-doc-home");

  if (isHome) {
    document.body.classList.add("pmx-home");
  }

  var menu = document.querySelector(".pmx-topbar__menu");
  var drawer = document.getElementById("__drawer");

  if (menu && drawer) {
    menu.addEventListener("click", function () {
      drawer.checked = !drawer.checked;
      menu.setAttribute("aria-expanded", drawer.checked ? "true" : "false");
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (event) {
      var id = anchor.getAttribute("href");
      if (!id || id.length < 2) {
        return;
      }
      var target = document.querySelector(id);
      if (!target) {
        return;
      }
      event.preventDefault();
      target.scrollIntoView({
        behavior: root.matches("[data-reduced-motion]") ? "auto" : "smooth",
      });
      history.replaceState(null, "", id);
    });
  });
})();

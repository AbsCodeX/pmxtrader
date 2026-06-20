/**
 * Platform hints for Mac / iOS styling and safe-area support.
 */
(function () {
  var root = document.documentElement;
  var ua = navigator.userAgent || "";
  var isApple =
    /Mac|iPhone|iPad|iPod/.test(ua) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

  if (isApple) {
    root.classList.add("is-apple");
  }
  if (/iPhone|iPad|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1)) {
    root.classList.add("is-ios");
  }
  if (/Mac/.test(ua) && !root.classList.contains("is-ios")) {
    root.classList.add("is-macos");
  }
})();

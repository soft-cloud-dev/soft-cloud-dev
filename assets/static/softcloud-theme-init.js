/**
 * assets/static/softcloud-theme-init.js
 * Synchronous early pre-paint theme initialization in <head> to prevent FOUC (WA-005, WA-THEME-001).
 * Immediately applies canonical Web Awesome theme classes: wa-dark or wa-light.
 */
(function () {
  try {
    var stored = localStorage.getItem('softcloud-theme') || localStorage.getItem('myst:theme');
    var isDark = false;
    if (stored === 'dark') {
      isDark = true;
    } else if (stored === 'light') {
      isDark = false;
    } else {
      isDark = Boolean(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }

    var root = document.documentElement;
    var targetTheme = isDark ? 'dark' : 'light';
    var targetWaClass = isDark ? 'wa-dark' : 'wa-light';
    var removeWaClass = isDark ? 'wa-light' : 'wa-dark';

    root.setAttribute('data-theme', targetTheme);
    root.classList.add(targetTheme);
    root.classList.remove(isDark ? 'light' : 'dark');
    root.classList.add(targetWaClass);
    root.classList.remove(removeWaClass);
    root.classList.remove('wa-theme-dark', 'wa-theme-light');
  } catch (e) {
    // Non-fatal if localStorage is restricted
  }
})();

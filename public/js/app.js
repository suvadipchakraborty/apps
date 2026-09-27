(() => {
  "use strict";

  const SITE_URL = "https://apps.suvadipchakraborty.workers.dev/";

  /* ---------------- theme ---------------- */

  const themeToggle = document.getElementById("themeToggle");
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  const THEME_COLORS = { light: "#faf8f3", dark: "#111218" };

  function setTheme(theme) {
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    themeToggle?.setAttribute("aria-pressed", String(theme === "dark"));
    themeToggle?.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
    if (metaThemeColor) metaThemeColor.setAttribute("content", THEME_COLORS[theme]);
    try {
      localStorage.setItem("shelf-theme", theme);
    } catch (err) {
      // storage may be unavailable — theme just won't persist
    }
  }

  themeToggle?.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    setTheme(isDark ? "light" : "dark");
  });

  // sync initial aria state + meta color (data-theme may already be set by the inline head script)
  setTheme(document.documentElement.hasAttribute("data-theme") ? "dark" : "light");

  /* ---------------- filters ---------------- */

  const chips = Array.from(document.querySelectorAll(".chip"));
  const cards = Array.from(document.querySelectorAll(".grid > *"));

  function applyFilter(filter) {
    cards.forEach((card) => {
      const cat = card.dataset.cat;
      const visible = filter === "all" || cat === filter || cat === "all";
      card.style.display = visible ? "" : "none";
    });
    chips.forEach((chip) => {
      chip.setAttribute("aria-pressed", String(chip.dataset.filter === filter));
    });
  }

  chips.forEach((chip) => {
    chip.addEventListener("click", () => applyFilter(chip.dataset.filter));
  });

  /* ---------------- toast ---------------- */

  const toastEl = document.getElementById("toast");
  let toastTimer = null;

  function showToast(message) {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2200);
  }

  /* ---------------- share ---------------- */

  const shareBtn = document.getElementById("shareBtn");

  shareBtn?.addEventListener("click", async () => {
    const shareData = {
      title: "The Shelf — small apps built by Suva",
      text: "A growing shelf of small, sharp apps — no logins, no bloat.",
      url: SITE_URL,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        // user cancelled the share sheet — nothing to do
      }
      return;
    }

    try {
      await navigator.clipboard.writeText(SITE_URL);
      showToast("Link copied");
    } catch (err) {
      showToast(SITE_URL);
    }
  });

  /* ---------------- save to home screen ---------------- */

  const installBtn = document.getElementById("installBtn");
  const installBackdrop = document.getElementById("installBackdrop");
  const sheetClose = document.getElementById("sheetClose");
  const sheetSteps = document.getElementById("sheetSteps");
  const sheetCopy = document.getElementById("sheetCopy");

  let deferredInstallPrompt = null;

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
  });

  function isStandalone() {
    return (
      window.matchMedia("(display-mode: standalone)").matches ||
      window.navigator.standalone === true
    );
  }

  function platformSteps() {
    const ua = window.navigator.userAgent || "";
    const isIOS = /iphone|ipad|ipod/i.test(ua);
    const isAndroid = /android/i.test(ua);
    const isSafari = /safari/i.test(ua) && !/chrome|crios|fxios/i.test(ua);

    if (isIOS && isSafari) {
      return [
        "Tap the Share icon in Safari's toolbar.",
        "Scroll down and tap \u201cAdd to Home Screen.\u201d",
        "Tap \u201cAdd\u201d to confirm.",
      ];
    }
    if (isIOS) {
      return [
        "Open this page in Safari (not this in-app browser).",
        "Tap the Share icon, then \u201cAdd to Home Screen.\u201d",
      ];
    }
    if (isAndroid) {
      return [
        "Tap the \u22ee menu in your browser.",
        "Choose \u201cAdd to Home screen\u201d or \u201cInstall app.\u201d",
        "Confirm to add it.",
      ];
    }
    return [
      "Look for an install icon in your browser's address bar.",
      "Or open the browser menu and choose \u201cInstall The Shelf.\u201d",
    ];
  }

  function openInstallSheet() {
    if (!installBackdrop) return;
    sheetCopy.textContent = "Install The Shelf like an app \u2014 one tap to reach it next time.";
    sheetSteps.innerHTML = "";
    platformSteps().forEach((step) => {
      const li = document.createElement("li");
      li.textContent = step;
      sheetSteps.appendChild(li);
    });
    installBackdrop.classList.add("show");
  }

  function closeInstallSheet() {
    installBackdrop?.classList.remove("show");
  }

  installBtn?.addEventListener("click", async () => {
    if (isStandalone()) {
      showToast("Already on your home screen");
      return;
    }

    if (deferredInstallPrompt) {
      deferredInstallPrompt.prompt();
      try {
        await deferredInstallPrompt.userChoice;
      } catch (err) {
        // ignore
      }
      deferredInstallPrompt = null;
      return;
    }

    openInstallSheet();
  });

  sheetClose?.addEventListener("click", closeInstallSheet);
  installBackdrop?.addEventListener("click", (event) => {
    if (event.target === installBackdrop) closeInstallSheet();
  });

  /* ---------------- service worker ---------------- */

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch(() => {
        // installability/offline is a bonus, not a requirement
      });
    });
  }
})();

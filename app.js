(() => {
  "use strict";

  const VERSION = "2.0";
  const SITE_URL = "https://apps.suvadipchakraborty.workers.dev/";
  const FEEDBACK_TO = "suvadipchakraborty@gmail.com";

  const $ = (sel, scope = document) => scope.querySelector(sel);
  const $$ = (sel, scope = document) => Array.from(scope.querySelectorAll(sel));
  const root = document.documentElement;

  /* ---------------- storage (never throws) ---------------- */

  const store = {
    get(key, fallback) {
      try {
        const raw = localStorage.getItem(key);
        return raw === null ? fallback : JSON.parse(raw);
      } catch (err) {
        return fallback;
      }
    },
    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch (err) {
        // storage unavailable: settings just won't persist
      }
    },
  };

  /* ---------------- toast ---------------- */

  const toastEl = $("#toast");
  let toastTimer = 0;
  function showToast(message) {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2200);
  }

  /* ---------------- preferences ---------------- */

  const DEFAULTS = { theme: "system", style: "vivid", layout: "tiles", sort: "curated", size: "md", motion: "system" };
  const THEME_COLORS = { light: "#f3f4fa", dark: "#0d0f1c" };
  const metaTheme = $('meta[name="theme-color"]');
  const darkQuery = window.matchMedia("(prefers-color-scheme: dark)");

  let prefs = (() => {
    const saved = store.get("shelf-prefs", null);
    const merged = Object.assign({}, DEFAULTS, saved || {});
    if (!saved) {
      // carry over the v1 light/dark choice so returning visitors keep their theme
      try {
        const legacy = localStorage.getItem("shelf-theme");
        if (legacy === "dark" || legacy === "light") merged.theme = legacy;
      } catch (err) {}
    }
    return merged;
  })();

  const resolvedTheme = () => (prefs.theme === "system" ? (darkQuery.matches ? "dark" : "light") : prefs.theme);

  function applyPrefs() {
    const theme = resolvedTheme();
    root.setAttribute("data-theme", theme);
    root.setAttribute("data-style", prefs.style);
    root.setAttribute("data-layout", prefs.layout);
    root.setAttribute("data-size", prefs.size);
    root.setAttribute("data-motion", prefs.motion);
    metaTheme?.setAttribute("content", THEME_COLORS[theme]);

    $("#themeQuick")?.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
    $$("[data-pref]").forEach((group) => {
      $$("button", group).forEach((btn) => {
        btn.setAttribute("aria-pressed", String(prefs[group.dataset.pref] === btn.dataset.value));
      });
    });
    $("#motionSwitch")?.setAttribute("aria-checked", String(prefs.motion === "reduce"));
  }

  function setPref(key, value) {
    prefs[key] = value;
    store.set("shelf-prefs", prefs);
    applyPrefs();
    if (key === "sort") applySort();
    renderExplore();
    refreshMailLinks();
  }

  darkQuery.addEventListener?.("change", () => {
    if (prefs.theme === "system") applyPrefs();
  });

  /* ---------------- app registry ---------------- */

  const list = $("#apps");
  const items = $$(".app", list);
  const heads = $$(".group-head", list);
  const byId = new Map(items.map((li) => [li.dataset.id, li]));
  const curated = items.slice().sort((a, b) => a.dataset.i - b.dataset.i);

  const tabEls = $$(".tab");
  const tabOrder = tabEls.map((t) => t.dataset.tab);
  const catLabel = {};
  tabEls.forEach((t) => {
    if (t.dataset.cat) catLabel[t.dataset.cat] = t.textContent.trim();
  });

  items.forEach((li) => {
    li.dataset.hay = [
      li.dataset.name,
      li.dataset.keys,
      $(".app-tag", li).textContent,
      $(".app-desc", li).textContent,
      catLabel[li.dataset.cat] || "",
    ].join(" ").toLowerCase();
  });

  const sortKey = (li) => li.dataset.name.replace(/^the\s+/i, "");

  function applySort() {
    if (prefs.sort === "az") {
      items
        .slice()
        .sort((a, b) => sortKey(a).localeCompare(sortKey(b), "en", { sensitivity: "base" }))
        .forEach((li) => list.appendChild(li));
      heads.forEach((h) => list.appendChild(h));
    } else {
      [...heads, ...items].sort((a, b) => a.dataset.i - b.dataset.i).forEach((n) => list.appendChild(n));
    }
  }

  /* ---------------- pins + recents ---------------- */

  let pins = store.get("shelf-pins", []).filter((id) => byId.has(id));
  let recent = store.get("shelf-recent", []).filter((id) => byId.has(id));
  const pinBadge = $("#pinBadge");

  function syncPins() {
    items.forEach((li) => {
      const on = pins.includes(li.dataset.id);
      li.dataset.pinned = on ? "1" : "";
      $(".pin", li)?.setAttribute("aria-pressed", String(on));
    });
    if (pinBadge) {
      pinBadge.textContent = String(pins.length);
      pinBadge.hidden = pins.length === 0;
    }
  }

  function togglePin(id) {
    const li = byId.get(id);
    if (!li) return;
    const name = li.dataset.name;
    if (pins.includes(id)) {
      pins = pins.filter((x) => x !== id);
      showToast(`Removed ${name} from My shelf`);
    } else {
      pins = [id, ...pins];
      showToast(`Pinned ${name} to My shelf`);
    }
    store.set("shelf-pins", pins);
    syncPins();
    if (state.view === "mine") renderMine();
  }

  function pushRecent(id) {
    if (!byId.has(id)) return;
    recent = [id, ...recent.filter((x) => x !== id)].slice(0, 8);
    store.set("shelf-recent", recent);
  }

  function renderMine() {
    const make = (id) => {
      const clone = byId.get(id).cloneNode(true);
      clone.hidden = false;
      clone.removeAttribute("data-hay");
      return clone;
    };
    const pinnedList = $("#pinnedList");
    const recentList = $("#recentList");
    pinnedList.replaceChildren(...pins.map(make));
    recentList.replaceChildren(...recent.map(make));

    const hasPins = pins.length > 0;
    const hasRecent = recent.length > 0;
    $("#mineEmpty").hidden = hasPins || hasRecent;
    $("#minePinned").hidden = !(hasPins || hasRecent);
    $("#pinnedHint").hidden = hasPins;
    pinnedList.hidden = !hasPins;
    $("#mineRecent").hidden = !hasRecent;
  }

  /* ---------------- explore: tabs + search ---------------- */

  const state = { view: "explore", tab: "all", q: "" };
  const tabsEl = $("#tabs");
  const tabsWrap = $("#tabsWrap");
  const searchInput = $("#q");
  const clearQ = $("#clearQ");
  const reduceMotion = () => root.getAttribute("data-motion") === "reduce" || window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function applyAccent() {
    let hue = "275";
    let hex = "#5a5bd6";
    if (state.view === "explore") {
      const active = $(`.tab[data-tab="${state.tab}"]`);
      if (active) {
        hue = active.dataset.h;
        hex = getComputedStyle(active).getPropertyValue("--fb2").trim() || hex;
      }
    }
    root.style.setProperty("--accent-h", hue);
    root.style.setProperty("--accent-hex", hex);
  }

  let booted = false;
  function renderExplore() {
    const terms = state.q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const searching = terms.length > 0;
    let shown = 0;

    items.forEach((li) => {
      const ok = searching
        ? terms.every((t) => li.dataset.hay.includes(t))
        : state.tab === "all" || li.dataset.cat === state.tab;
      li.hidden = !ok;
      if (ok) shown += 1;
    });

    const grouped = !searching && state.tab === "all" && prefs.sort === "curated";
    heads.forEach((h) => (h.hidden = !grouped));

    tabsWrap.hidden = searching;
    $("#pick").hidden = searching || state.tab !== "all";
    $("#endNote").hidden = searching;
    clearQ.hidden = !state.q;

    const line = $("#resultLine");
    line.hidden = !searching;
    if (searching) line.textContent = `${shown} ${shown === 1 ? "app matches" : "apps match"} “${state.q.trim()}”`;

    const empty = $("#searchEmpty");
    empty.hidden = !(searching && shown === 0);
    if (!empty.hidden) $("#emptyQ").textContent = state.q.trim();

    $("#panel").setAttribute("aria-labelledby", `tab-${state.tab}`);

    if (!booted) {
      let n = 0;
      items.forEach((li) => {
        if (!li.hidden && n < 16) li.style.setProperty("--n", String(n++));
      });
    }
  }

  function setTab(tab, opts = {}) {
    if (!tabOrder.includes(tab)) tab = "all";
    state.tab = tab;
    tabEls.forEach((t) => {
      const on = t.dataset.tab === tab;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
    });
    applyAccent();
    renderExplore();

    const active = $(`.tab[data-tab="${tab}"]`);
    if (active && opts.scrollTab !== false) {
      tabsEl.scrollTo({
        left: active.offsetLeft - (tabsEl.clientWidth - active.offsetWidth) / 2,
        behavior: reduceMotion() ? "auto" : "smooth",
      });
    }

    if (opts.dir && !reduceMotion()) {
      list.classList.remove("swap-l", "swap-r");
      void list.offsetWidth;
      list.classList.add(opts.dir === "l" ? "swap-l" : "swap-r");
    }

    if (opts.keepScroll !== true) {
      const top = $("#tabsSentinel").getBoundingClientRect().top + window.scrollY;
      if (window.scrollY > top) window.scrollTo(0, top);
    }
    syncUrl();
  }

  tabEls.forEach((t) => {
    t.addEventListener("click", () => setTab(t.dataset.tab));
    t.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      const next = tabOrder.indexOf(t.dataset.tab) + (e.key === "ArrowRight" ? 1 : -1);
      if (next < 0 || next >= tabOrder.length) return;
      setTab(tabOrder[next]);
      $(`.tab[data-tab="${tabOrder[next]}"]`).focus();
    });
  });

  // swipe left/right on the list to move between tabs
  (() => {
    const area = $("#exploreBody");
    let sx = 0, sy = 0, st = 0;
    area.addEventListener("touchstart", (e) => {
      if (e.touches.length !== 1) return;
      sx = e.touches[0].clientX;
      sy = e.touches[0].clientY;
      st = Date.now();
    }, { passive: true });
    area.addEventListener("touchend", (e) => {
      if (state.q.trim()) return;
      const t = e.changedTouches[0];
      const dx = t.clientX - sx;
      const dy = t.clientY - sy;
      if (Math.abs(dx) < 70 || Math.abs(dx) < Math.abs(dy) * 1.8 || Date.now() - st > 650) return;
      const next = tabOrder.indexOf(state.tab) + (dx < 0 ? 1 : -1);
      if (next >= 0 && next < tabOrder.length) setTab(tabOrder[next], { dir: dx < 0 ? "l" : "r", keepScroll: true });
    }, { passive: true });
  })();

  searchInput.addEventListener("input", () => {
    state.q = searchInput.value;
    renderExplore();
  });
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Escape") clearSearch();
    if (e.key === "Enter") searchInput.blur();
  });
  clearQ.addEventListener("click", () => {
    clearSearch();
    searchInput.focus();
  });
  function clearSearch() {
    searchInput.value = "";
    state.q = "";
    renderExplore();
  }

  // shadow under the sticky tab bar only once it is actually stuck
  (() => {
    const sentinel = $("#tabsSentinel");
    const cover = $(".status-cover");
    let ticking = false;
    const update = () => {
      ticking = false;
      const inset = cover ? cover.offsetHeight : 0;
      tabsWrap.classList.toggle("stuck", sentinel.getBoundingClientRect().top <= inset);
    };
    window.addEventListener("scroll", () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    }, { passive: true });
  })();

  /* ---------------- today's pick ---------------- */

  function renderPick() {
    const host = $("#pick");
    const now = new Date();
    const day = Math.floor((now.getTime() - now.getTimezoneOffset() * 60000) / 86400000);
    const pool = curated.slice(2); // never duplicate the first row
    const li = pool[(day * 7) % pool.length];
    if (!li) return;
    const a = document.createElement("a");
    a.className = "pick";
    a.href = $(".app-link", li).href;
    a.target = "_blank";
    a.rel = "noopener";
    a.dataset.id = li.dataset.id;
    a.dataset.cat = li.dataset.cat;
    a.style.setProperty("--o", li.style.getPropertyValue("--o") || "0");
    a.innerHTML =
      '<span class="app-icon" aria-hidden="true">' + $(".glyph", li).outerHTML + "</span>" +
      '<span class="pick-text"><span class="pick-label">Today\u2019s pick</span>' +
      '<span class="pick-name"></span><span class="pick-tag"></span></span>' +
      '<span class="pick-go">Open</span>';
    $(".pick-name", a).textContent = li.dataset.name;
    $(".pick-tag", a).textContent = $(".app-tag", li).textContent;
    host.replaceChildren(a);
  }

  /* ---------------- views + navigation ---------------- */

  const views = { explore: $("#view-explore"), mine: $("#view-mine"), settings: $("#view-settings") };
  const dockButtons = $$("#dock button");

  function showView(name, opts = {}) {
    state.view = name;
    Object.keys(views).forEach((key) => (views[key].hidden = key !== name));
    dockButtons.forEach((btn) => {
      if (btn.dataset.view === name) btn.setAttribute("aria-current", "page");
      else btn.removeAttribute("aria-current");
    });
    if (name === "mine") renderMine();
    if (name === "settings") {
      refreshMailLinks();
      refreshInstallUi();
    }
    applyAccent();
    if (opts.animate !== false) {
      const el = views[name];
      el.classList.remove("enter");
      void el.offsetWidth;
      el.classList.add("enter");
    }
    if (opts.scroll !== false) window.scrollTo(0, 0);
    syncUrl();
  }

  dockButtons.forEach((btn) => btn.addEventListener("click", () => showView(btn.dataset.view)));
  document.addEventListener("click", (e) => {
    const go = e.target.closest("[data-go]");
    if (go) showView(go.dataset.go);
  });

  function syncUrl() {
    let qs = "";
    if (state.view === "mine") qs = "?tab=mine";
    else if (state.view === "settings") qs = "?tab=settings";
    else if (state.tab !== "all") qs = `?tab=${state.tab}`;
    try {
      history.replaceState(null, "", location.pathname + qs);
    } catch (err) {}
  }

  /* ---------------- clicks: pin, open, long-press ---------------- */

  let suppressUntil = 0;
  let lastPointer = "mouse";

  document.addEventListener("click", (e) => {
    const pin = e.target.closest(".pin");
    if (pin) {
      togglePin(pin.dataset.id);
      return;
    }
    const link = e.target.closest(".app-link, .pick");
    if (!link) return;
    if (Date.now() < suppressUntil) {
      e.preventDefault();
      return;
    }
    const holder = link.closest("[data-id]");
    if (holder) pushRecent(holder.dataset.id);
  });

  document.addEventListener("auxclick", (e) => {
    if (e.button !== 1) return;
    const link = e.target.closest(".app-link, .pick");
    const holder = link && link.closest("[data-id]");
    if (holder) pushRecent(holder.dataset.id);
  });

  // press and hold an app (touch/pen) to pin it, handy in the Icons layout
  (() => {
    let timer = 0;
    let origin = null;
    const cancel = () => {
      clearTimeout(timer);
      origin = null;
    };
    document.addEventListener("pointerdown", (e) => {
      lastPointer = e.pointerType;
      if (e.pointerType === "mouse") return;
      const link = e.target.closest(".app-link");
      if (!link) return;
      origin = { x: e.clientX, y: e.clientY };
      clearTimeout(timer);
      timer = setTimeout(() => {
        const holder = link.closest("[data-id]");
        if (!holder) return;
        suppressUntil = Date.now() + 800;
        togglePin(holder.dataset.id);
        if (navigator.vibrate) navigator.vibrate(12);
      }, 520);
    }, { passive: true });
    document.addEventListener("pointermove", (e) => {
      if (origin && Math.hypot(e.clientX - origin.x, e.clientY - origin.y) > 10) cancel();
    }, { passive: true });
    document.addEventListener("pointerup", cancel, { passive: true });
    document.addEventListener("pointercancel", cancel, { passive: true });
    document.addEventListener("contextmenu", (e) => {
      if (lastPointer !== "mouse" && e.target.closest(".app-link")) e.preventDefault();
    });
  })();

  $("#clearRecent")?.addEventListener("click", () => {
    recent = [];
    store.set("shelf-recent", recent);
    renderMine();
  });

  /* ---------------- settings controls ---------------- */

  $$("[data-pref]").forEach((group) => {
    $$("button", group).forEach((btn) => {
      btn.addEventListener("click", () => setPref(group.dataset.pref, btn.dataset.value));
    });
  });

  $("#motionSwitch")?.addEventListener("click", () => {
    setPref("motion", prefs.motion === "reduce" ? "system" : "reduce");
  });

  $("#themeQuick")?.addEventListener("click", () => {
    setPref("theme", resolvedTheme() === "dark" ? "light" : "dark");
  });

  function twoStep(button, subEl, action) {
    const original = subEl.textContent;
    let armed = false;
    let timer = 0;
    const disarm = () => {
      armed = false;
      clearTimeout(timer);
      button.classList.remove("confirm");
      subEl.textContent = original;
    };
    button.addEventListener("click", () => {
      if (!armed) {
        armed = true;
        button.classList.add("confirm");
        subEl.textContent = "Tap again to confirm";
        timer = setTimeout(disarm, 3500);
        return;
      }
      disarm();
      action();
    });
  }

  twoStep($("#clearDataRow"), $("#clearDataSub"), () => {
    pins = [];
    recent = [];
    store.set("shelf-pins", pins);
    store.set("shelf-recent", recent);
    syncPins();
    showToast("Pins and recent apps cleared");
  });

  twoStep($("#resetRow"), $("#resetSub"), () => {
    prefs = Object.assign({}, DEFAULTS);
    store.set("shelf-prefs", prefs);
    applyPrefs();
    applySort();
    renderExplore();
    showToast("Settings reset");
  });

  $("#updateRow")?.addEventListener("click", async () => {
    showToast("Checking for updates\u2026");
    try {
      const reg = await navigator.serviceWorker?.getRegistration();
      await reg?.update();
    } catch (err) {
      // offline: reload will fall back to the cached copy
    }
    setTimeout(() => location.reload(), 700);
  });

  /* ---------------- feedback email (pre-filled) ---------------- */

  const MAIL = {
    feedback: {
      subject: "Feedback on The Shelf",
      body: "Hi Suva,\n\nWhat I was trying to do:\n\n\nWhat happened, or what I'd change:\n\n",
    },
    broken: {
      subject: "Broken app on The Shelf",
      body: "Hi Suva,\n\nWhich app is broken:\n\nWhat went wrong:\n\nWhat I expected:\n\n",
    },
    idea: {
      subject: "App idea for The Shelf",
      body: "Hi Suva,\n\nMy app idea, in one line:\n\nWho it would help:\n\nWhy it would be useful:\n\n",
    },
  };

  function deviceInfo() {
    const ua = navigator.userAgent || "";
    const os = /android/i.test(ua) ? "Android"
      : /iphone|ipad|ipod/i.test(ua) ? "iOS"
      : /windows/i.test(ua) ? "Windows"
      : /mac os/i.test(ua) ? "macOS"
      : /linux/i.test(ua) ? "Linux" : "Unknown OS";
    const browser = /edg\//i.test(ua) ? "Edge"
      : /(crios|chrome)\//i.test(ua) ? "Chrome"
      : /(fxios|firefox)\//i.test(ua) ? "Firefox"
      : /safari/i.test(ua) ? "Safari" : "browser";
    return `${os}, ${browser}`;
  }

  function mailHref(kind) {
    const m = MAIL[kind] || MAIL.feedback;
    const footer = [
      "",
      "---",
      `Sent from The Shelf ${VERSION}`,
      `${deviceInfo()}, ${window.innerWidth}x${window.innerHeight}`,
      `${isStandalone() ? "Installed on home screen" : "Opened in browser"}, ${resolvedTheme()} theme, ${prefs.layout} view`,
    ].join("\n");
    const body = (m.body + footer).replace(/\n/g, "\r\n");
    return `mailto:${FEEDBACK_TO}?subject=${encodeURIComponent(m.subject)}&body=${encodeURIComponent(body)}`;
  }

  function refreshMailLinks() {
    $$("[data-mail]").forEach((a) => (a.href = mailHref(a.dataset.mail)));
  }

  // capture phase: href is fresh before the browser follows it
  document.addEventListener("click", (e) => {
    const a = e.target.closest("[data-mail]");
    if (a) a.href = mailHref(a.dataset.mail);
  }, true);

  /* ---------------- share ---------------- */

  async function shareSite() {
    const data = {
      title: "The Shelf \u2014 small apps built by Suva",
      text: "A growing shelf of small, sharp apps \u2014 no logins, no bloat.",
      url: SITE_URL,
    };
    if (navigator.share) {
      try {
        await navigator.share(data);
      } catch (err) {
        // share sheet dismissed
      }
      return;
    }
    try {
      await navigator.clipboard.writeText(SITE_URL);
      showToast("Link copied");
    } catch (err) {
      showToast(SITE_URL);
    }
  }
  $("#shareBtn")?.addEventListener("click", shareSite);
  $("#shareRow")?.addEventListener("click", shareSite);

  /* ---------------- save to home screen ---------------- */

  const installBackdrop = $("#installBackdrop");
  const sheetSteps = $("#sheetSteps");
  const installNote = $("#installNote");
  let deferredInstallPrompt = null;

  function isStandalone() {
    return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  }

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
  });

  window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
    showToast("Added to your home screen");
    refreshInstallUi();
  });

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
    sheetSteps.innerHTML = "";
    platformSteps().forEach((step) => {
      const li = document.createElement("li");
      li.textContent = step;
      sheetSteps.appendChild(li);
    });
    installBackdrop.classList.add("show");
  }
  const closeInstallSheet = () => installBackdrop.classList.remove("show");

  async function triggerInstall() {
    if (isStandalone()) {
      showToast("Already on your home screen");
      return;
    }
    if (deferredInstallPrompt) {
      deferredInstallPrompt.prompt();
      try {
        await deferredInstallPrompt.userChoice;
      } catch (err) {}
      deferredInstallPrompt = null;
      return;
    }
    openInstallSheet();
  }

  function refreshInstallUi() {
    const standalone = isStandalone();
    const sub = $("#installSub");
    if (sub) sub.textContent = standalone ? "Installed on this device" : "Open The Shelf like an app";
    if (installNote) installNote.hidden = standalone || store.get("shelf-install-dismissed", false);
  }

  $("#installRow")?.addEventListener("click", triggerInstall);
  $("#installNoteBtn")?.addEventListener("click", triggerInstall);
  $("#installNoteClose")?.addEventListener("click", () => {
    store.set("shelf-install-dismissed", true);
    installNote.hidden = true;
  });
  $("#sheetClose")?.addEventListener("click", closeInstallSheet);
  installBackdrop?.addEventListener("click", (e) => {
    if (e.target === installBackdrop) closeInstallSheet();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeInstallSheet();
  });

  /* ---------------- boot ---------------- */

  const versionLabel = $("#versionLabel");
  if (versionLabel) versionLabel.textContent = VERSION;

  applyPrefs();
  applySort();
  syncPins();
  renderPick();
  refreshMailLinks();
  refreshInstallUi();

  (() => {
    const params = new URLSearchParams(location.search);
    const want = params.get("tab");
    if (want === "mine" || want === "settings") {
      setTab("all", { scrollTab: false, keepScroll: true });
      showView(want, { animate: false, scroll: false });
    } else {
      setTab(tabOrder.includes(want) ? want : "all", { scrollTab: false, keepScroll: true });
      showView("explore", { animate: false, scroll: false });
      const q = params.get("q");
      if (q) {
        searchInput.value = q;
        state.q = q;
        renderExplore();
      }
    }
    // centre the active tab once layout has settled
    requestAnimationFrame(() => {
      const active = $(".tab[aria-selected='true']");
      if (active && state.tab !== "all") tabsEl.scrollLeft = active.offsetLeft - (tabsEl.clientWidth - active.offsetWidth) / 2;
    });
  })();

  booted = true;
  setTimeout(() => root.classList.remove("boot"), 1500);

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) renderPick();
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

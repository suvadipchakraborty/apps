// Bump this string on every deploy that changes a file in SHELL_FILES.
// Network-first below means this mostly matters for offline fallback,
// not for freshness — but bump it anyway so old caches get pruned.
const SHELL_CACHE = "shelf-shell-v14";
const SHELL_FILES = [
  "/",
  "/index.html",
  "/css/styles.css",
  "/js/app.js",
  "/fonts/bricolage-latin.woff2",
  "/fonts/figtree-latin.woff2",
  "/manifest.webmanifest",
  "/favicon.ico",
  "/assets/icon-192.png",
];

self.addEventListener("install", (event) => {
  // Cache each file on its own so one missing file can never block the update.
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) =>
      Promise.all(SHELL_FILES.map((file) => cache.add(file).catch(() => {})))
    )
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== SHELL_CACHE).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// Network-first for everything same-origin: a deploy is always visible on
// next load, and the cache only kicks in when the network fails (offline).
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin) return;

  const isPage = event.request.mode === "navigate";

  event.respondWith(
    fetch(event.request)
      .then((res) => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(SHELL_CACHE).then((cache) => cache.put(event.request, clone));
        }
        return res;
      })
      .catch(async () => {
        // Home-screen shortcuts open /?tab=mine etc., so ignore the query offline.
        const hit = await caches.match(event.request, { ignoreSearch: isPage });
        if (hit) return hit;
        if (isPage) return (await caches.match("/")) || (await caches.match("/index.html"));
        return Response.error();
      })
  );
});

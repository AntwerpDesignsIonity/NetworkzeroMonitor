/*
 * NetworkzeroMonitor - Service Worker
 * Ionity (Pty) Ltd - www.ionity.today
 *
 * Caches the app shell for offline launch / installability. Live API
 * calls (/api/*) are always network-first so monitoring data stays fresh.
 */

const CACHE = 'nzm-shell-v1';
const SHELL = [
  '.',
  'index.html',
  'styles.css',
  'app.js',
  'icon.svg',
  'manifest.webmanifest',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API requests: network-first (monitoring data must be live).
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request).catch(() =>
      new Response(JSON.stringify({ error: 'offline' }), {
        headers: { 'Content-Type': 'application/json' },
        status: 503,
      })
    ));
    return;
  }

  // App shell: cache-first with background refresh.
  event.respondWith(
    caches.match(event.request).then((cached) =>
      cached || fetch(event.request).then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((cache) => cache.put(event.request, copy)).catch(() => {});
        return resp;
      }).catch(() => cached)
    )
  );
});

const CACHE_NAME = 'quickbill-v1';
const urlsToCache = [
  '/',
    '/static/style.css',
    '/static/bootstrap.min.css',
  '/static/icons/icon.png',
  '/static/icons/icon2.png'
];

// Install SW
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

// Fetch from cache
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

const CACHE_NAME = 'android-foss-v0.0.14';
const CORE_ASSETS = [
	'./',
	'index.html',
	'assets/styles.css',
	'assets/app.js',
	'assets/brand/android-foss-mark.png',
	'assets/icons/favicon-32.png',
	'assets/icons/apple-touch-icon.png',
	'assets/icons/icon-192.png',
	'assets/icons/icon-512.png',
	'catalog.json',
	'catalog-trust.json',
	'catalog-popularity.json',
	'README.md',
];

self.addEventListener('install', event => {
	event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS)));
	self.skipWaiting();
});

self.addEventListener('activate', event => {
	event.waitUntil(
		caches.keys()
			.then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
			.then(() => self.clients.claim())
	);
});

self.addEventListener('fetch', event => {
	if (event.request.method !== 'GET') return;
	event.respondWith(
		fetch(event.request)
			.then(response => {
				if (response.ok && new URL(event.request.url).origin === self.location.origin) {
					const copy = response.clone();
					caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
				}
				return response;
			})
			.catch(() => caches.match(event.request).then(cached => cached || caches.match('index.html')))
	);
});

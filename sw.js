self.addEventListener("install", e => {
  e.waitUntil(
    caches.open("lampada-cache").then(cache => {
      return cache.addAll([
        "./",
        "./index.html"
      ]);
    })
  );
});
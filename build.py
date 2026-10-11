"""把 index.html（claude.ai Artifact 用的頁面片段）打包成可獨立部署的 PWA，輸出到 docs/。

GitHub Pages 從 main 分支的 /docs 發佈。改完 index.html 後執行：python build.py
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
VERSION = "v5"  # 每次改版調高，讓 service worker 換掉舊快取

HEAD = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#c8281e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="選號器">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-180.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""

TAIL = """
<script>
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
</script>
</body>
</html>
"""

SW = """const CACHE = 'scratch-picker-%s';
const FILES = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'icon-180.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// 網路優先：有網路就拿最新版，離線時用快取
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request).then(res => {
      if (res.ok && new URL(e.request.url).origin === location.origin) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match(e.request))
  );
});
""" % VERSION

MANIFEST = {
    "name": "刮刮樂選號器",
    "short_name": "選號器",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#f7f2ec",
    "theme_color": "#c8281e",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
}


def make_icon(size: int, path: Path) -> None:
    img = Image.new("RGB", (size, size), "#c8281e")
    d = ImageDraw.Draw(img)
    m = size * 0.16
    d.rounded_rectangle([m, m, size - m, size - m], radius=size * 0.08, fill="#fbefd0", outline="#b9860b", width=max(2, size // 64))
    try:
        font = ImageFont.truetype("arialbd.ttf", int(size * 0.34))
    except OSError:
        font = ImageFont.load_default()
    d.text((size / 2, size / 2), "888", fill="#c8281e", font=font, anchor="mm")
    img.save(path)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    (OUT / "index.html").write_text(HEAD + page + TAIL, encoding="utf-8")
    (OUT / "sw.js").write_text(SW, encoding="utf-8")
    (OUT / "manifest.webmanifest").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")
    for s in (180, 192, 512):
        make_icon(s, OUT / f"icon-{s}.png")
    (OUT / ".nojekyll").write_text("")
    print("built", OUT)


if __name__ == "__main__":
    main()

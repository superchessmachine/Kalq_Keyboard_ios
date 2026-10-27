#!/bin/zsh
# Render build/kalq.js with the real KeymanWeb engine and screenshot it -> layout.png
# Needs Google Chrome and a network connection (the engine loads from Keyman's CDN).
set -e
cd "$(dirname "$0")/.."
[ -f build/kalq.js ] || { echo "run kmc build first"; exit 1 }
W=$(mktemp -d); cp build/kalq.js tools/preview.html "$W/"; mv "$W/preview.html" "$W/index.html"
(cd "$W" && python3 -m http.server 8731 >/dev/null 2>&1 &)
SRV=$!; sleep 1
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-sandbox \
  --window-size=786,520 --user-agent="$UA" --virtual-time-budget=9000 \
  --screenshot="$W/raw.png" http://localhost:8731/index.html 2>/dev/null
pkill -f "http.server 8731" || true
python3 -c "
from PIL import Image
im = Image.open('$W/raw.png').convert('RGB')
bg = im.getpixel((im.width - 2, im.height - 2))   # trim the empty frame below the keys
px = im.load()
bottom = im.height
while bottom > 1 and all(px[x, bottom - 1] == bg for x in range(0, im.width, 7)):
    bottom -= 1
im.crop((0, 0, im.width, min(bottom + 8, im.height))).save('layout.png')
print('wrote layout.png', im.width, 'x', bottom + 8)
"
rm -rf "$W"

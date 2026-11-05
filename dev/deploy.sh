#!/bin/bash
# Uso: ./deploy.sh "mensaje"
set -e
cd /home/claude/drone-rush
V=$(date -u +%Y%m%d%H%M%S)
(printf '<!doctype html>\n'; sed "s/__BUILD__/$V/" ../drone-rush.html) > index.html
echo "$V" > version.txt
# versión para portales web (CrazyGames / Poki): sin Telegram ni Monetag
mkdir -p crazygames
python3 - "$V" <<'PY'
import sys
s=open('/home/claude/drone-rush.html').read().replace('__BUILD__',sys.argv[1])
s=s.replace('<script src="https://telegram.org/js/telegram-web-app.js"></script>\n','<script>window.CG_BUILD=true</script>\n<script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>\n')
s=s.replace('<script src="https://libtl.com/sdk.js" data-zone="12015673" data-sdk="show_12015673"></script>\n','')
assert 'CG_BUILD' in s and 'libtl' not in s
open('/home/claude/drone-rush/crazygames/index.html','w').write('<!doctype html>\n'+s)
import os
src=open('/home/claude/drone-rush.html').read().replace('__BUILD__',sys.argv[1])
src=src.replace('<script src="https://telegram.org/js/telegram-web-app.js"></script>\n','<script>window.POKI_BUILD=true</script>\n<script src="https://game-cdn.poki.com/scripts/v2/poki-sdk.js"></script>\n')
src=src.replace('<script src="https://libtl.com/sdk.js" data-zone="12015673" data-sdk="show_12015673"></script>\n','')
assert 'POKI_BUILD' in src and 'libtl' not in src and 'telegram-web-app' not in src
os.makedirs('/home/claude/drone-rush/poki',exist_ok=True)
open('/home/claude/drone-rush/poki/index.html','w').write('<!doctype html>\n'+src)
PY
git add -A
git commit -qm "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R7NJW5oqCduCfzyTmgEete"
git push -q
git log --oneline -1

#!/bin/bash
# ============================================================
# DataHub 自動更新（伺服器版）
# 2026-11-26 重寫：原本寫死 /home/tree/...（樹的電腦），改成伺服器路徑
#
# 認證：Google service account（service_account.json，已在 .gitignore）
# 推���：GitHub credential store（repo 外，remote URL 不含 token）
# ============================================================
set -uo pipefail

HUB_DIR="/home/node/.openclaw/workspace/projects/datahub"
LOGFILE="/home/node/.openclaw/workspace/log/datahub.log"
STATUSFILE="/home/node/.openclaw/workspace/log/datahub.status"

mkdir -p "$(dirname "$LOGFILE")"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"; }

cd "$HUB_DIR" || { log "❌ 目錄不存在：$HUB_DIR"; exit 1; }

# ── 憑證前置檢查：沒有 service_account.json 就直接失敗，不要假裝成功 ──
if [ ! -f "service_account.json" ]; then
  log "❌ 缺少 service_account.json（Google Drive service account）"
  echo "error missing-credentials $(date -u +%FT%TZ)" > "$STATUSFILE"
  exit 1
fi

log "📁 更新 gallery.json（Google Drive）…"
python3 - << 'PYEOF' || { echo "❌ gallery.json 更新失敗" >&2; exit 1; }
import sys, json
sys.path.insert(0, '.')
from gallery import list_date_folders, list_images_in_folder

folders = list_date_folders()
if not folders:
    print("❌ 無法取得資料夾列表（憑證無效或 Drive 無回應）")
    sys.exit(1)

gallery_data = {}
for folder in folders:
    date = folder['date']
    images = list_images_in_folder(folder['id'])
    gallery_data[date] = {
        'count': len(images),
        'images': [{'name': i['name'], 'url': i['url'], 'thumbnail': i['thumbnail']} for i in images]
    }
    print(f"  📁 {date}: {len(images)} 張圖片")

with open('gallery.json', 'w', encoding='utf-8') as f:
    json.dump(gallery_data, f, ensure_ascii=False, indent=2)
print(f"✅ gallery.json 已更新（{len(gallery_data)} 個日期）")
PYEOF

log "🧩 嵌入 index.html…"
python3 - << 'PYEOF' || { echo "❌ index.html 嵌入失敗" >&2; exit 1; }
import json

with open('gallery.json', 'r', encoding='utf-8') as f:
    gallery_raw = json.load(f)

dates = []
for date_str, data in sorted(gallery_raw.items(), reverse=True):
    images = []
    for img in data.get('images', []):
        url = img.get('url', '')
        if '/file/d/' in url:
            file_id = url.split('/file/d/')[1].split('/')[0]
            img['direct_url'] = f'https://drive.google.com/uc?export=view&id={file_id}'
        images.append(img)
    dates.append({'date': date_str, 'folder_id': '', 'count': data.get('count', 0), 'images': images})

gallery_data = {'dates': dates}

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old1 = 'let galleryData = { dates: [] };'
new1 = f'let galleryData = {json.dumps(gallery_data, ensure_ascii=False, indent=8)};'
content = content.replace(old1, new1, 1)

func_start = content.find('async function loadGalleryData()')
if func_start != -1:
    depth = 0
    i = content.find('{', func_start)
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    func_end = i + 1
    new_func = '''function loadGalleryData() {
            galleryData = JSON.parse(JSON.stringify(GALLERY_DATA));
            populateDateSelector();
            document.getElementById('update-time').textContent = new Date().toLocaleString('zh-TW');
        }'''
    content = content[:func_start] + new_func + content[func_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✅ index.html 已嵌入數據（{len(dates)} 個日期）")
PYEOF

git add gallery.json index.html 2>/dev/null
if git diff --cached --quiet; then
  log "ℹ️ 內容無變更，不產生 commit"
  echo "ok nochange $(date -u +%FT%TZ)" > "$STATUSFILE"
  exit 0
fi

git commit -q -m "Auto update: $(date '+%Y-%m-%d %H:%M')" || { log "❌ commit 失敗"; exit 1; }

if git push origin main 2>&1 | tee -a "$LOGFILE"; then
  SHA=$(git rev-parse --short HEAD)
  log "✅ 已推送：$SHA"
  echo "ok $SHA $(date -u +%FT%TZ)" > "$STATUSFILE"
else
  log "❌ push 失敗"
  echo "error push-failed $(date -u +%FT%TZ)" > "$STATUSFILE"
  exit 1
fi

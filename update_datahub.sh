#!/bin/bash
# DataHub 自動完整更新腳本
# 更新 gallery.json → 嵌入 index.html → 提交 GitHub

set -e

cd /home/tree/.openclaw/workspace/datahub

# 激活 virtualenv（如果有的話）
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

echo "[$(date)] 開始更新 DataHub..."

# 1. 更新 gallery.json（從 Google Drive 讀取）
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from gallery import list_date_folders, list_images_in_folder
import json

folders = list_date_folders()
if not folders:
    print("❌ 無法取得資料夾列表")
    exit(1)

gallery_data = {}
for folder in folders:
    date = folder['date']
    images = list_images_in_folder(folder['id'])
    gallery_data[date] = {
        'count': len(images),
        'images': [{'name': img['name'], 'url': img['url'], 'thumbnail': img['thumbnail']} for img in images]
    }
    print(f"  📁 {date}: {len(images)} 張圖片")

with open('gallery.json', 'w', encoding='utf-8') as f:
    json.dump(gallery_data, f, ensure_ascii=False, indent=2)

print(f"✅ gallery.json 已更新（{len(gallery_data)} 個日期）")
PYEOF

if [ $? -ne 0 ]; then
    echo "❌ gallery.json 更新失敗"
    exit 1
fi

# 2. 嵌入 gallery.json 到 index.html
python3 << 'PYEOF'
import json, re

with open('gallery.json', 'r', encoding='utf-8') as f:
    gallery_raw = json.load(f)

# 轉換格式（按日期排序，最新的在前）
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

# 1. 替換 let galleryData = { dates: [] };
old1 = 'let galleryData = { dates: [] };'
new1 = f'let galleryData = {json.dumps(gallery_data, ensure_ascii=False, indent=8)};'
content = content.replace(old1, new1, 1)

# 2. 替換整個 async function loadGalleryData() 區塊
func_start = content.find('async function loadGalleryData()')
if func_start != -1:
    depth = 0
    func_start_brace = content.find('{', func_start)
    i = func_start_brace
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

if [ $? -ne 0 ]; then
    echo "❌ index.html 嵌入失敗"
    exit 1
fi

# 3. 提交並推送到 GitHub
git add -A
git commit -m "Auto update: $(date +%Y-%m-%d)"

# 直接使用 git push（remote origin 已設定好 token）
git push 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 已推送到 GitHub"
else
    echo "⚠️ Push 失敗，請檢查網路或 token"
fi

echo "[$(date)] DataHub 更新完成！"

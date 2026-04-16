#!/usr/bin/env python3
"""把 gallery.json 嵌入到 index.html，同時轉換為直接連結"""

import json
import os

# 讀取 gallery.json
gallery_path = os.path.join(os.path.dirname(__file__), "gallery.json")
with open(gallery_path, 'r', encoding='utf-8') as f:
    gallery_data = json.load(f)

# 轉換 Google Drive 連結為直接下載連結
for date_obj in gallery_data['dates']:
    for img in date_obj['images']:
        url = img.get('url', '')
        if '/file/d/' in url:
            file_id = url.split('/file/d/')[1].split('/')[0]
            img['direct_url'] = f'https://drive.google.com/uc?export=view&id={file_id}'
        else:
            img['direct_url'] = url

# 讀取 index.html
html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 建立嵌入的數據
embedded_data = json.dumps(gallery_data, ensure_ascii=False, indent=8)

# 1. 替換 let galleryData = { dates: [] }; 這一行
old1 = 'let galleryData = { dates: [] };'
new1 = f'let galleryData = {embedded_data};'
html_content = html_content.replace(old1, new1)

# 2. 替換 async function loadGalleryData() 區塊
# 找到開始位置
start_marker = 'async function loadGalleryData() {'
end_marker = '// Populate date selector'

start_idx = html_content.find(start_marker)
end_idx = html_content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_func = '''function loadGalleryData() {
            galleryData = JSON.parse(JSON.stringify(GALLERY_DATA));
            populateDateSelector();
            document.getElementById('update-time').textContent = new Date().toLocaleString('zh-TW');
        }
'''
    # 找到 function loadGalleryData() 的結束位置 (倒序找最後一個 })
    # 從 start_idx 開始找到第一個 {
    brace_start = html_content.find('{', start_idx)
    # 然後找到對應的結束 }
    depth = 0
    end_brace = brace_start
    for i in range(brace_start, len(html_content)):
        if html_content[i] == '{':
            depth += 1
        elif html_content[i] == '}':
            depth -= 1
            if depth == 0:
                end_brace = i
                break
    
    # 替換
    old_func = html_content[brace_start:end_brace+1]
    html_content = html_content.replace(old_func, new_func)

# 寫回
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ gallery.json 已嵌入 HTML（包含 direct_url）")
print(f"   日期數: {len(gallery_data['dates'])}")
print(f"   總圖片: {sum(d['count'] for d in gallery_data['dates'])}")

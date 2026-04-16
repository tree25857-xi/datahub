#!/usr/bin/env python3
"""把 gallery.json 嵌入到 index.html，同時轉換為直接連結"""

import json
import os

# 取得腳本所在目錄
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 讀取 gallery.json
gallery_path = os.path.join(SCRIPT_DIR, 'gallery.json')
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
html_path = os.path.join(SCRIPT_DIR, 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 替換 let galleryData = { dates: [] }; 為 const GALLERY_DATA = ...
old1 = 'let galleryData = { dates: [] };'
new1 = f'const GALLERY_DATA = {json.dumps(gallery_data, ensure_ascii=False, indent=8)};'
content = content.replace(old1, new1, 1)

# 2. 替換整個 async function loadGalleryData() 區塊
func_start = content.find('async function loadGalleryData()')
if func_start != -1:
    # 找到函數結束位置（計算括號深度）
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
    
    # 新函數
    new_func = '''function loadGalleryData() {
            galleryData = JSON.parse(JSON.stringify(GALLERY_DATA));
            populateDateSelector();
            document.getElementById('update-time').textContent = new Date().toLocaleString('zh-TW');
        }'''
    
    content = content[:func_start] + new_func + content[func_end:]

# 寫回
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ gallery.json 已嵌入 HTML（包含 direct_url）")
print(f"   日期數: {len(gallery_data['dates'])}")
print(f"   總圖片: {sum(d['count'] for d in gallery_data['dates'])}")

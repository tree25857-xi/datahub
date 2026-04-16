#!/usr/bin/env python3
"""修補 index_corrupted.html：修復圖庫的 thumbnail 和 loadGalleryData"""

import json
import re

GALLERY_JSON = '/home/tree/.openclaw/workspace/datahub/gallery.json'
CORRUPTED = '/home/tree/Desktop/temp/index_corrupted.html'
OUTPUT = '/home/tree/Desktop/temp/index_fixed.html'

# 讀取 gallery.json
with open(GALLERY_JSON, 'r', encoding='utf-8') as f:
    gallery_data = json.load(f)

# 修復 thumbnail URL
for date_obj in gallery_data['dates']:
    for img in date_obj['images']:
        url = img.get('url', '')
        file_id = None
        if '/file/d/' in url:
            file_id = url.split('/file/d/')[1].split('/')[0]
        if file_id:
            img['thumbnail'] = f'https://drive.google.com/thumbnail?id={file_id}&sz=s400'
            img['direct_url'] = f'https://drive.google.com/uc?export=view&id={file_id}'

# 讀取 corrupted
with open(CORRUPTED, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修復 GALLERY_DATA → let galleryData
gallery_data_start = content.find('const GALLERY_DATA = {')
gallery_data_end = content.find('};', gallery_data_start) + 2

new_gallery_data = 'let galleryData = ' + json.dumps(gallery_data, ensure_ascii=False, indent=8) + ';'
content = content[:gallery_data_start] + new_gallery_data + content[gallery_data_end:]

# 2. 移除所有 loadGalleryData 中的 GALLERY_DATA 引用（替換為正確版本）
#    正確的 loadGalleryData 不需要 GALLERY_DATA
correct_func = '''function loadGalleryData() {
            populateDateSelector();
            document.getElementById('update-time').textContent = new Date().toLocaleString('zh-TW');
        }'''

# 移除所有 loadGalleryData 函數，然後在正確位置插入一份
content = re.sub(r'function loadGalleryData\(\)[^{]*\{(?:[^{}]|\{[^{}]*\})*\}', '', content)

# 3. 移除多餘的 let galleryData = { dates: [] };
content = re.sub(r'\n\s*let galleryData = \{ dates: \[\] \};', '', content)

# 4. 在 populateDateSelector 之前插入正確的 loadGalleryData
pop_pos = content.find('function populateDateSelector()')
if pop_pos != -1:
    content = content[:pop_pos] + correct_func + '\n\n        ' + content[pop_pos:]

# 5. 確保只有一個 loadGalleryData
funcs = re.findall(r'function loadGalleryData\(\)', content)
print(f"✅ loadGalleryData 函數數量: {len(funcs)}")

# 6. 驗證
print(f"✅ GALLERY_DATA 引用數: {content.count('GALLERY_DATA')}")
print(f"✅ sz=s400 thumbnail 數: {content.count('sz=s400')}")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ 已生成: {OUTPUT}")
print(f"   日期數: {len(gallery_data['dates'])}")
print(f"   總圖片: {sum(d['count'] for d in gallery_data['dates'])}")
print(f"   thumbnail: sz=s400")
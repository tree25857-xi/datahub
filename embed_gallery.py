#!/usr/bin/env python3
"""把 gallery.json 嵌入到 index.html，同時轉換為直接連結"""

import json
import os
import re

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
embedded_script = f'''<script>
        // Embedded gallery data with direct URLs
        const GALLERY_DATA = {json.dumps(gallery_data, ensure_ascii=False, indent=8)};
        
        function loadGalleryData() {{
            galleryData = GALLERY_DATA;
            populateDateSelector();
            document.getElementById('update-time').textContent = new Date().toLocaleString('zh-TW');
        }}
</script>'''

# 替換 loadGalleryData 函數
pattern = r'async function loadGalleryData\(\).*?// Initialize'
replacement = embedded_script

new_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

# 寫回
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("✅ gallery.json 已嵌入 HTML（包含 direct_url）")
print(f"   日期數: {len(gallery_data['dates'])}")
print(f"   總圖片: {sum(d['count'] for d in gallery_data['dates'])}")
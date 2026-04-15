#!/usr/bin/env python3
"""Fix gallery URLs and embed into index.html"""

import json
import os
import re

# Read and convert gallery.json
gallery_path = os.path.join(os.path.dirname(__file__), "gallery.json")
with open(gallery_path, 'r', encoding='utf-8') as f:
    gallery_data = json.load(f)

# Add direct_url to each image
for date_obj in gallery_data['dates']:
    for img in date_obj['images']:
        url = img.get('url', '')
        if '/file/d/' in url:
            file_id = url.split('/file/d/')[1].split('/')[0]
            img['direct_url'] = f'https://drive.google.com/uc?export=view&id={file_id}'
        else:
            img['direct_url'] = url

# Read index.html
html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find GALLERY_DATA line and replace with processed data
old_pattern = r'const GALLERY_DATA = \{.*?\};'
new_data = json.dumps(gallery_data, ensure_ascii=False)

new_html = re.sub(old_pattern, f'const GALLERY_DATA = {new_data};', html_content, flags=re.DOTALL)

# Write back
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("✅ Gallery fixed with direct_url")
print(f"   Dates: {len(gallery_data['dates'])}")
print(f"   Total images: {sum(d['count'] for d in gallery_data['dates'])}")

# Verify
with open(html_path, 'r') as f:
    content = f.read()
if 'direct_url' in content and 'uc?export=view&id=' in content:
    print("✅ direct_url found in HTML")
else:
    print("❌ direct_url NOT found in HTML")
#!/usr/bin/env python3
"""
生成 gallery.json - DataHub 圖庫資料
"""

import sys
import json
import os

sys.path.insert(0, os.path.dirname(__file__))

from gallery import list_date_folders, list_images_in_folder

def generate_gallery_json():
    """生成圖庫 JSON 資料"""
    
    folders = list_date_folders()
    
    gallery_data = {
        "updated": None,
        "dates": []
    }
    
    for folder in folders:
        images = list_images_in_folder(folder['id'])
        gallery_data["dates"].append({
            "date": folder['date'],
            "folder_id": folder['id'],
            "count": len(images),
            "images": [
                {
                    "name": img['name'],
                    "url": img['url'],
                    "thumbnail": img['thumbnail'],
                    "created": img['created']
                }
                for img in images
            ]
        })
    
    # 寫入 JSON 檔案
    output_path = os.path.join(os.path.dirname(__file__), "gallery.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(gallery_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成 gallery.json")
    print(f"   日期數: {len(gallery_data['dates'])}")
    print(f"   總圖片: {sum(d['count'] for d in gallery_data['dates'])}")
    
    return gallery_data

if __name__ == '__main__':
    generate_gallery_json()
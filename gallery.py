#!/usr/bin/env python3
"""
Google Drive Gallery - 曦曦圖庫
讀取 Google Drive 資料夾中的圖片
"""

import os
import json
from datetime import datetime

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Google Drive 設定
FOLDER_ID = "1R_sojJTif-X7wwTGDaoXFozqTH7fQCgW"
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "service_account.json")

def get_credentials():
    """取得 Google 認證"""
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    return service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )

def list_date_folders():
    """列出所有日期子資料夾"""
    credentials = get_credentials()
    if not credentials:
        return []
    
    try:
        service = build('drive', 'v3', credentials=credentials)
        
        # 取得根目錄中的所有子資料夾（命名為日期格式）
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder'",
            pageSize=100,
            fields="files(id, name, createdTime)"
        ).execute()
        
        folders = []
        for f in results.get('files', []):
            folders.append({
                'name': f['name'],
                'id': f['id'],
                'date': f['name']  # 資料夾名稱就是日期
            })
        
        # 按日期排序（新的在前）
        folders.sort(key=lambda x: x['date'], reverse=True)
        return folders
        
    except Exception as e:
        print(f"Error listing folders: {e}")
        return []

def list_images_in_folder(folder_id):
    """列出特定資料夾中的所有圖片"""
    credentials = get_credentials()
    if not credentials:
        return []
    
    try:
        service = build('drive', 'v3', credentials=credentials)
        
        results = service.files().list(
            q=f"'{folder_id}' in parents and (mimeType contains 'image/' or mimeType='image/jpeg' or mimeType='image/png' or mimeType='image/gif' or mimeType='image/webp')",
            pageSize=100,
            fields="files(id, name, mimeType, createdTime, webViewLink, thumbnailLink)"
        ).execute()
        
        images = []
        for f in results.get('files', []):
            # 取得 Google Drive 原始縮圖 URL
            thumbnail = f.get('thumbnailLink', '')
            
            images.append({
                'id': f['id'],
                'name': f['name'],
                'mimeType': f.get('mimeType', ''),
                'created': f.get('createdTime', '')[:19],
                'url': f.get('webViewLink', ''),
                'thumbnail': thumbnail
            })
        
        return images
        
    except Exception as e:
        print(f"Error listing images: {e}")
        return []

def get_gallery_data(date_str=None):
    """取得指定日期的圖片列表"""
    
    if not GOOGLE_API_AVAILABLE:
        return {"error": "Google API 未可用", "images": []}
    
    if not os.path.exists(CREDENTIALS_PATH):
        return {"error": "服務帳號憑證不存在", "images": []}
    
    try:
        folders = list_date_folders()
        
        if date_str:
            # 找特定日期的資料夾
            target_folder = None
            for folder in folders:
                if folder['date'] == date_str:
                    target_folder = folder
                    break
            
            if not target_folder:
                return {
                    "date": date_str,
                    "found": False,
                    "images": [],
                    "message": f"找不到日期 {date_str} 的資料夾"
                }
            
            images = list_images_in_folder(target_folder['id'])
            return {
                "date": date_str,
                "found": True,
                "count": len(images),
                "images": images
            }
        else:
            # 返回所有日期列表
            return {
                "dates": [f['date'] for f in folders],
                "count": len(folders)
            }
            
    except Exception as e:
        return {"error": str(e), "images": []}

if __name__ == '__main__':
    print("📁 曦曦圖庫 - Google Drive 讀取測試")
    print("-" * 50)
    
    # 列出所有日期
    folders = list_date_folders()
    print(f"找到 {len(folders)} 個日期資料夾:")
    for folder in folders[:10]:
        print(f"  📁 {folder['date']}")
    
    if len(folders) > 10:
        print(f"  ... 還有 {len(folders) - 10} 個")
    
    # 測試讀取第一個日期的圖片
    if folders:
        sample = folders[0]
        print(f"\n📅 讀取 {sample['date']} 的圖片:")
        images = list_images_in_folder(sample['id'])
        print(f"  找到 {len(images)} 張圖片")
        for img in images[:3]:
            print(f"  🖼️ {img['name']}")
            print(f"     縮圖: {img['thumbnail'][:50]}...")
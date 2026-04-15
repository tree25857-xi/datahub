#!/usr/bin/env python3
"""Fix JavaScript in index.html"""

import re

with open('/home/tree/.openclaw/workspace/datahub/index.html', 'r') as f:
    content = f.read()

old_section = '''        async function loadGalleryData() {
            // Use embedded data directly
            galleryData = GALLERY_DATA;
            populateDateSelector();
            document.getElementById('update-time').textContent = new Date().toLocaleString('zh-TW');
        }
</script>
        window.onload = function() {
            loadGalleryData();
        };'''

new_section = '''        function populateDateSelector() {
            const select = document.getElementById('gallery-date');
            select.innerHTML = '';
            
            if (galleryData.dates && galleryData.dates.length > 0) {
                galleryData.dates.forEach(dateObj => {
                    const option = document.createElement('option');
                    option.value = dateObj.date;
                    option.textContent = dateObj.date + ' (' + dateObj.count + '張)';
                    select.appendChild(option);
                });
                
                if (galleryData.dates.length > 0) {
                    select.value = galleryData.dates[0].date;
                    loadGallery();
                }
            } else {
                select.innerHTML = '<option value="">無可用日期</option>';
            }
        }
        
        function loadGallery() {
            const dateStr = document.getElementById('gallery-date').value;
            const grid = document.getElementById('gallery-grid');
            const countSpan = document.getElementById('gallery-count');
            
            if (!dateStr) {
                grid.innerHTML = '<div class="gallery-loading">請選擇日期</div>';
                return;
            }
            
            const dateData = galleryData.dates.find(d => d.date === dateStr);
            
            if (!dateData || !dateData.images || dateData.images.length === 0) {
                grid.innerHTML = '<div class="gallery-loading">該日期無圖片</div>';
                countSpan.textContent = '';
                return;
            }
            
            currentImages = dateData.images;
            countSpan.textContent = '共 ' + currentImages.length + ' 張圖片';
            
            grid.innerHTML = '';
            currentImages.forEach((img, index) => {
                const item = document.createElement('div');
                item.className = 'gallery-item';
                item.onclick = () => openLightbox(index);
                
                if (img.thumbnail) {
                    item.innerHTML = '<img src="' + img.thumbnail + '" alt="' + img.name + '" loading="lazy">';
                } else {
                    item.innerHTML = '<div class="gallery-loading">📷</div>';
                }
                
                const nameDiv = document.createElement('div');
                nameDiv.className = 'img-name';
                nameDiv.textContent = img.name;
                item.appendChild(nameDiv);
                
                grid.appendChild(item);
            });
        }
        
        function openLightbox(index) {
            currentIndex = index;
            const img = currentImages[index];
            document.getElementById('lightbox-img').src = img.url || img.thumbnail;
            document.getElementById('lightbox-info').textContent = img.name;
            document.getElementById('lightbox').classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeLightbox() {
            document.getElementById('lightbox').classList.remove('active');
            document.body.style.overflow = '';
        }
        
        function navigateImage(direction) {
            currentIndex += direction;
            if (currentIndex < 0) currentIndex = currentImages.length - 1;
            if (currentIndex >= currentImages.length) currentIndex = 0;
            const img = currentImages[currentIndex];
            document.getElementById('lightbox-img').src = img.url || img.thumbnail;
            document.getElementById('lightbox-info').textContent = img.name;
        }
        
        async function loadGalleryData() {
            galleryData = GALLERY_DATA;
            populateDateSelector();
            document.getElementById('update-time').textContent = new Date().toLocaleString('zh-TW');
        }
        
        document.addEventListener('keydown', function(e) {
            if (document.getElementById('lightbox').classList.contains('active')) {
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowLeft') navigateImage(-1);
                if (e.key === 'ArrowRight') navigateImage(1);
            }
        });
        
        document.getElementById('lightbox').addEventListener('click', function(e) {
            if (e.target === this) closeLightbox();
        });
        
        window.onload = function() {
            loadGalleryData();
        };'''

content = content.replace(old_section, new_section)

with open('/home/tree/.openclaw/workspace/datahub/index.html', 'w') as f:
    f.write(content)

print("✅ JavaScript 已修復")
#!/usr/bin/env python3
import os
import shutil
from PIL import Image
from pathlib import Path

def compress_images():
    source_dir = Path('test_images')
    backup_dir = Path('test_images_old')
    
    if backup_dir.exists():
        print(f"Удаляем старый backup {backup_dir}...")
        shutil.rmtree(backup_dir)
    
    print(f"Создаем backup: {source_dir} -> {backup_dir}")
    shutil.copytree(source_dir, backup_dir)
    
    max_dimension = 1200
    quality = 85
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    total_original_size = 0
    total_compressed_size = 0
    processed_count = 0
    
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext not in image_extensions:
                continue
            
            filepath = Path(root) / filename
            
            try:
                original_size = filepath.stat().st_size
                total_original_size += original_size
                
                with Image.open(filepath) as img:
                    original_mode = img.mode
                    width, height = img.size
                    
                    if width <= max_dimension and height <= max_dimension:
                        print(f"✓ {filepath.relative_to(source_dir)}: уже оптимального размера ({width}x{height})")
                        continue
                    
                    ratio = min(max_dimension / width, max_dimension / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    
                    print(f"⚙ {filepath.relative_to(source_dir)}: {width}x{height} -> {new_width}x{new_height}")
                    
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    if img_resized.mode == 'RGBA' and ext in {'.jpg', '.jpeg'}:
                        background = Image.new('RGB', img_resized.size, (255, 255, 255))
                        background.paste(img_resized, mask=img_resized.split()[3])
                        img_resized = background
                    
                    save_kwargs = {'quality': quality, 'optimize': True}
                    if ext == '.png':
                        save_kwargs = {'optimize': True}
                    
                    img_resized.save(filepath, **save_kwargs)
                    
                    compressed_size = filepath.stat().st_size
                    total_compressed_size += compressed_size
                    processed_count += 1
                    
                    reduction = (1 - compressed_size / original_size) * 100
                    print(f"  Размер: {original_size//1024}KB -> {compressed_size//1024}KB (-{reduction:.1f}%)")
            
            except Exception as e:
                print(f"✗ Ошибка обработки {filepath}: {e}")
    
    if processed_count > 0:
        total_reduction = (1 - total_compressed_size / total_original_size) * 100
        print(f"\n{'='*60}")
        print(f"Обработано изображений: {processed_count}")
        print(f"Исходный размер: {total_original_size // (1024*1024)} MB")
        print(f"Сжатый размер: {total_compressed_size // (1024*1024)} MB")
        print(f"Общее сжатие: {total_reduction:.1f}%")
        print(f"Backup сохранен в: {backup_dir}")
    else:
        print("\nВсе изображения уже оптимального размера!")

if __name__ == '__main__':
    compress_images()

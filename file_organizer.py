#!/usr/bin/env python3
"""
📊 FILE ORGANIZER OTOMATIS
Auto-organize files di Download folder berdasarkan tipe
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

def print_banner():
    banner = """
==================================================
📊 FILE ORGANIZER OTOMATIS
==================================================
"""
    print(banner)

# Kategori file berdasarkan ekstensi
FILE_CATEGORIES = {
    'Videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp'],
    'Music': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.opus'],
    'Pictures': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.heic'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
    'Apps': ['.apk', '.xapk', '.apks'],
    'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.json', '.xml', '.sh'],
    'Ebooks': ['.epub', '.mobi', '.azw', '.azw3', '.fb2'],
}

def get_file_hash(filepath):
    """Generate MD5 hash untuk deteksi duplikat"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def get_category(filename):
    """Tentukan kategori file berdasarkan ekstensi"""
    ext = Path(filename).suffix.lower()
    
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    
    return 'Others'  # Kategori default

def organize_files(source_dir, dry_run=False, remove_duplicates=False):
    """Organize files ke folder kategori"""
    
    if not os.path.exists(source_dir):
        print(f"[!] Folder tidak ditemukan: {source_dir}")
        return
    
    print(f"[*] Scanning folder: {source_dir}")
    print(f"[*] Mode: {'DRY RUN (Preview Only)' if dry_run else 'ORGANIZE'}")
    print(f"[*] Remove Duplicates: {'YES' if remove_duplicates else 'NO'}")
    print("="*50)
    
    # Statistik
    stats = {
        'moved': 0,
        'skipped': 0,
        'duplicates': 0,
        'errors': 0,
        'by_category': {}
    }
    
    # Tracking duplikat
    file_hashes = {}
    
    # Scan semua file
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    
    if not files:
        print("[!] Tidak ada file ditemukan!")
        return
    
    print(f"[+] Ditemukan {len(files)} file\n")
    
    for filename in files:
        filepath = os.path.join(source_dir, filename)
        
        # Skip file organizer sendiri
        if filename == os.path.basename(__file__):
            continue
        
        # Tentukan kategori
        category = get_category(filename)
        
        # Buat folder kategori jika belum ada
        category_dir = os.path.join(source_dir, category)
        
        try:
            # Cek duplikat jika diminta
            if remove_duplicates:
                file_hash = get_file_hash(filepath)
                
                if file_hash and file_hash in file_hashes:
                    duplicate_path = file_hashes[file_hash]
                    print(f"[~] DUPLICATE: {filename}")
                    print(f"    Same as: {os.path.basename(duplicate_path)}")
                    
                    if not dry_run:
                        os.remove(filepath)
                        print(f"    ✓ Deleted")
                    
                    stats['duplicates'] += 1
                    continue
                
                if file_hash:
                    file_hashes[file_hash] = filepath
            
            # Buat folder kategori
            if not dry_run and not os.path.exists(category_dir):
                os.makedirs(category_dir)
            
            # Tentukan path tujuan
            dest_path = os.path.join(category_dir, filename)
            
            # Handle jika file sudah ada di tujuan
            if os.path.exists(dest_path):
                # Tambahkan timestamp ke nama file
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{name}_{timestamp}{ext}"
                dest_path = os.path.join(category_dir, new_filename)
            
            # Move file
            print(f"[→] {filename}")
            print(f"    Category: {category}")
            
            if not dry_run:
                shutil.move(filepath, dest_path)
                print(f"    ✓ Moved")
            else:
                print(f"    → Would move to: {category}/")
            
            stats['moved'] += 1
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
        except Exception as e:
            print(f"[!] ERROR: {filename}")
            print(f"    {str(e)}")
            stats['errors'] += 1
        
        print()
    
    # Tampilkan statistik
    print("\n" + "="*50)
    print("📊 STATISTIK")
    print("="*50)
    print(f"[+] Total File Processed : {len(files)}")
    print(f"[+] Successfully Moved   : {stats['moved']}")
    print(f"[+] Duplicates Removed   : {stats['duplicates']}")
    print(f"[+] Errors               : {stats['errors']}")
    
    if stats['by_category']:
        print("\n[+] Files by Category:")
        for category, count in sorted(stats['by_category'].items()):
            print(f"    {category:15} : {count} file(s)")
    
    print("="*50)
    
    if dry_run:
        print("\n💡 Ini adalah DRY RUN (preview only)")
        print("   Jalankan tanpa '--dry-run' untuk benar-benar organize file")

def clean_empty_folders(source_dir):
    """Hapus folder kosong setelah organize"""
    print(f"\n[*] Cleaning empty folders...")
    
    removed = 0
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        
        if os.path.isdir(item_path):
            try:
                # Cek apakah folder kosong
                if not os.listdir(item_path):
                    os.rmdir(item_path)
                    print(f"[+] Removed empty folder: {item}")
                    removed += 1
            except:
                pass
    
    if removed > 0:
        print(f"[+] Removed {removed} empty folder(s)")
    else:
        print("[+] No empty folders found")

def undo_organize(source_dir):
    """Undo organize - kembalikan semua file ke root folder"""
    print(f"[*] Undoing organization...")
    print("="*50)
    
    moved = 0
    
    # Loop semua folder kategori
    for category in FILE_CATEGORIES.keys():
        category_dir = os.path.join(source_dir, category)
        
        if not os.path.exists(category_dir):
            continue
        
        print(f"[*] Processing: {category}/")
        
        for filename in os.listdir(category_dir):
            filepath = os.path.join(category_dir, filename)
            
            if os.path.isfile(filepath):
                dest_path = os.path.join(source_dir, filename)
                
                # Handle jika file sudah ada
                if os.path.exists(dest_path):
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_filename = f"{name}_{timestamp}{ext}"
                    dest_path = os.path.join(source_dir, new_filename)
                
                try:
                    shutil.move(filepath, dest_path)
                    print(f"    [←] {filename}")
                    moved += 1
                except Exception as e:
                    print(f"    [!] Error moving {filename}: {e}")
    
    print("\n" + "="*50)
    print(f"[+] Moved back {moved} file(s)")
    print("="*50)
    
    # Clean empty folders
    clean_empty_folders(source_dir)

def main():
    import argparse
    
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='Organize files di Download folder berdasarkan tipe',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='/storage/emulated/0/Download',
        help='Path folder yang mau di-organize (default: /storage/emulated/0/Download)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview aja tanpa move file (testing mode)'
    )
    
    parser.add_argument(
        '--remove-duplicates',
        action='store_true',
        help='Hapus file duplikat (berdasarkan MD5 hash)'
    )
    
    parser.add_argument(
        '--undo',
        action='store_true',
        help='Undo organize - kembalikan semua file ke root folder'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Hapus folder kosong setelah organize'
    )
    
    args = parser.parse_args()
    
    source_dir = args.path
    
    if args.undo:
        confirm = input("[?] Yakin mau undo organize? (y/n): ")
        if confirm.lower() == 'y':
            undo_organize(source_dir)
        else:
            print("[!] Undo dibatalkan")
    elif args.clean:
        clean_empty_folders(source_dir)
    else:
        organize_files(source_dir, dry_run=args.dry_run, remove_duplicates=args.remove_duplicates)
        
        if not args.dry_run:
            print("\n✅ Organize selesai!")
            
            if not args.remove_duplicates:
                print("\n💡 Tip: Gunakan '--remove-duplicates' untuk hapus file duplikat")

if __name__ == "__main__":
    main()

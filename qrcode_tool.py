#!/usr/bin/env python3
"""
📱 QR CODE GENERATOR & READER
Generate QR code dari text/URL & decode QR dari gambar
"""

import sys
import os
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

def print_banner():
    banner = """
==================================================
📱 QR CODE GENERATOR & READER
==================================================
"""
    print(banner)

def generate_qr(data, filename=None, show_terminal=True):
    """Generate QR Code"""
    print(f"[*] Generating QR Code...")
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,  # Auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Tampilkan di terminal (ASCII art)
    if show_terminal:
        print("\n" + "="*50)
        print("📲 QR CODE (ASCII Preview)")
        print("="*50)
        qr.print_ascii(invert=True)
        print("="*50)
    
    # Save ke file jika diminta
    if filename:
        # Pastikan path lengkap ke Download
        if not filename.startswith('/'):
            download_path = '/storage/emulated/0/Download'
            filename = os.path.join(download_path, filename)
        
        # Pastikan ekstensi .png
        if not filename.lower().endswith('.png'):
            filename += '.png'
        
        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        
        print(f"\n[+] QR Code tersimpan: {filename}")
        print(f"[+] Ukuran file: {os.path.getsize(filename)} bytes")
    
    print("\n✅ QR Code berhasil dibuat!")

def read_qr(image_path):
    """Read/Decode QR Code dari gambar"""
    print(f"[*] Reading QR Code from: {image_path}")
    
    try:
        # Buka gambar
        img = Image.open(image_path)
        
        # Decode QR code
        decoded_objects = decode(img)
        
        if not decoded_objects:
            print("[!] Tidak ada QR Code ditemukan di gambar ini!")
            return
        
        print("\n" + "="*50)
        print(f"📖 HASIL DECODE ({len(decoded_objects)} QR Code ditemukan)")
        print("="*50)
        
        for i, obj in enumerate(decoded_objects, 1):
            data = obj.data.decode('utf-8')
            qr_type = obj.type
            
            print(f"\n[QR Code #{i}]")
            print(f"[+] Type      : {qr_type}")
            print(f"[+] Data      : {data}")
            print(f"[+] Position  : {obj.rect}")
            
            # Deteksi tipe data
            if data.startswith('http://') or data.startswith('https://'):
                print(f"[+] Detected  : URL/Link")
            elif data.startswith('WIFI:'):
                print(f"[+] Detected  : WiFi Credentials")
            elif '@' in data and '.' in data:
                print(f"[+] Detected  : Email")
            elif data.startswith('tel:'):
                print(f"[+] Detected  : Phone Number")
            else:
                print(f"[+] Detected  : Plain Text")
        
        print("\n" + "="*50)
        print("✅ Decode berhasil!")
        
    except FileNotFoundError:
        print(f"[!] File tidak ditemukan: {image_path}")
    except Exception as e:
        print(f"[!] Error: {e}")

def generate_wifi_qr(ssid, password, security="WPA", hidden=False, filename=None):
    """Generate QR Code untuk WiFi credentials"""
    print(f"[*] Generating WiFi QR Code...")
    
    # Format WiFi QR: WIFI:T:WPA;S:MySSID;P:MyPassword;H:false;;
    hidden_str = "true" if hidden else "false"
    wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden_str};;"
    
    print(f"\n[+] SSID      : {ssid}")
    print(f"[+] Password  : {'*' * len(password)}")
    print(f"[+] Security  : {security}")
    print(f"[+] Hidden    : {hidden}")
    
    generate_qr(wifi_string, filename, show_terminal=True)
    print("\n💡 Tip: Scan QR ini dengan HP untuk auto-connect ke WiFi!")

def generate_vcard_qr(name, phone, email=None, filename=None):
    """Generate QR Code untuk kontak (vCard)"""
    print(f"[*] Generating Contact QR Code...")
    
    # Format vCard 3.0
    vcard = f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\nTEL:{phone}\n"
    
    if email:
        vcard += f"EMAIL:{email}\n"
    
    vcard += "END:VCARD"
    
    print(f"\n[+] Name  : {name}")
    print(f"[+] Phone : {phone}")
    if email:
        print(f"[+] Email : {email}")
    
    generate_qr(vcard, filename, show_terminal=True)
    print("\n💡 Tip: Scan QR ini untuk langsung save kontak!")

def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print("📖 Cara Pakai:")
        print("\n1️⃣ GENERATE QR CODE dari text/URL:")
        print("   python qrcode_tool.py generate \"text atau URL\" [output.png]")
        print("\n2️⃣ READ/DECODE QR CODE dari gambar:")
        print("   python qrcode_tool.py read <path_ke_gambar>")
        print("\n3️⃣ GENERATE WiFi QR CODE:")
        print("   python qrcode_tool.py wifi \"SSID\" \"Password\" [output.png]")
        print("   python qrcode_tool.py wifi \"MyWiFi\" \"pass123\" wifi_qr.png")
        print("\n4️⃣ GENERATE Contact QR CODE (vCard):")
        print("   python qrcode_tool.py contact \"Nama\" \"08123456789\" [email] [output.png]")
        print("\nContoh:")
        print("   python qrcode_tool.py generate \"https://github.com\" github_qr.png")
        print("   python qrcode_tool.py generate \"Halo, ini pesanku!\"")
        print("   python qrcode_tool.py read /sdcard/Download/qr_image.jpg")
        print("   python qrcode_tool.py wifi \"RumahKu\" \"password123\" my_wifi.png")
        print("   python qrcode_tool.py contact \"John Doe\" \"081234567890\" \"john@email.com\"")
        print("="*50)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "generate" or command == "gen" or command == "g":
        if len(sys.argv) < 3:
            print("[!] Error: Data untuk QR Code tidak diberikan!")
            print("    Contoh: python qrcode_tool.py generate \"Hello World\"")
            sys.exit(1)
        
        data = sys.argv[2]
        filename = sys.argv[3] if len(sys.argv) > 3 else None
        
        generate_qr(data, filename)
    
    elif command == "read" or command == "decode" or command == "r":
        if len(sys.argv) < 3:
            print("[!] Error: Path gambar tidak diberikan!")
            print("    Contoh: python qrcode_tool.py read /sdcard/Download/qr.jpg")
            sys.exit(1)
        
        image_path = sys.argv[2]
        read_qr(image_path)
    
    elif command == "wifi" or command == "w":
        if len(sys.argv) < 4:
            print("[!] Error: SSID dan Password tidak lengkap!")
            print("    Contoh: python qrcode_tool.py wifi \"MyWiFi\" \"password123\"")
            sys.exit(1)
        
        ssid = sys.argv[2]
        password = sys.argv[3]
        filename = sys.argv[4] if len(sys.argv) > 4 else None
        
        generate_wifi_qr(ssid, password, filename=filename)
    
    elif command == "contact" or command == "vcard" or command == "c":
        if len(sys.argv) < 4:
            print("[!] Error: Nama dan nomor telepon tidak lengkap!")
            print("    Contoh: python qrcode_tool.py contact \"John\" \"081234567890\"")
            sys.exit(1)
        
        name = sys.argv[2]
        phone = sys.argv[3]
        
        # Cek apakah ada email atau langsung filename
        email = None
        filename = None
        
        if len(sys.argv) > 4:
            if '@' in sys.argv[4]:  # Kemungkinan email
                email = sys.argv[4]
                filename = sys.argv[5] if len(sys.argv) > 5 else None
            else:  # Kemungkinan langsung filename
                filename = sys.argv[4]
        
        generate_vcard_qr(name, phone, email, filename)
    
    else:
        print(f"[!] Command tidak dikenal: {command}")
        print("    Gunakan: generate, read, wifi, atau contact")
        sys.exit(1)
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main()

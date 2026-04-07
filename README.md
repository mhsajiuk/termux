# 🛠️ Kumpulan Script Termux Seru & Berguna

Repo ini berisi kumpulan script Python CLI ringan yang didesain khusus buat dijalankan di Termux Android. Ada *tools* buat gaya-gayaan (Prank/Art) sampai *tools* fungsional yang ngebantu hidup lo sehari-hari!

---

## ⚙️ Persiapan Awal (Wajib Lakukan Sekali)

Sebelum bisa pakai semua *script* di repo ini, pastikan lo udah setup Termux lo. Jalankan perintah di bawah ini secara berurutan:

### **1. Izinkan Akses Penyimpanan (Biar file bisa di-save/baca dari HP):**
```bash
termux-setup-storage
```

### **2. Update Termux & Install Semua Kebutuhan (Python, Git, FFmpeg, dll):**
```bash
pkg update && pkg upgrade -y
pkg install python git libjpeg-turbo ffmpeg yt-dlp zbar -y
```

> **⚠️ PENTING:** 
> - **FFmpeg** wajib diinstall buat downloader video! Tanpa FFmpeg, download video YouTube/sosmed bakal error.
> - **zbar** diperlukan buat QR Code reader (decode QR dari gambar).

### **3. Clone Repository Ini & Masuk ke Foldernya:**
```bash
git clone https://github.com/USERNAME_LU/NAMA_REPO_LU.git
cd NAMA_REPO_LU
```

### **4. Install Library Python:**
```bash
pip install -r requirements.txt
```

---

## 1️⃣ 🖼️ ASCII Art Generator (ascii_maker.py)

Script simpel buat ngubah foto atau gambar apa aja jadi seni teks ASCII langsung di layar terminal! Cocok banget buat seru-seruan, pamer ke temen, atau dijadiin *welcome screen* (MOTD) di Termux.

### **✨ Fitur:**
 * **Auto-Ratio:** Gambar nggak melar karena menyesuaikan tinggi *font* terminal.
 * **Auto-Save:** Hasil langsung disave ke hasil_ascii.txt biar gampang di-copy.
 * **Dark Mode Ready:** Karakter udah disesuaikan buat background hitam Termux.

### **🚀 Cara Pakai:**
```bash
python ascii_maker.py /storage/emulated/0/Download/foto_kamu.jpg
```

*(Tips: Gunakan posisi HP landscape/tidur dan foto close-up untuk hasil terbaik!)*

---

## 2️⃣ 🚀 Ultimate Sosmed Downloader (dwnld.py)

Download video atau ekstrak lagu (MP3) dari YouTube, TikTok, Instagram, Twitter, dan ribuan situs lainnya langsung dari terminal HP kamu. Nggak ada lagi iklan pop-up ngeganggu! Semua file otomatis masuk ke folder Download di HP lo.

### **✨ Fitur:**
 * **All-in-One:** Support hampir semua link sosmed.
 * **Auto-Merge:** Menggabungkan video & audio kualitas terbaik secara otomatis (thanks to FFmpeg).
 * **MP3 Extractor:** Bisa langsung convert video YouTube/TikTok jadi lagu MP3.

### **🚀 Cara Pakai:**

**Download Video (Kualitas Tertinggi):**
```bash
python dwnld.py "LINK_VIDEO_DISINI"
```

**Download Audio/Lagunya Saja (Format MP3):**
*Tambahkan bendera -a atau --audio di belakang*
```bash
python dwnld.py "LINK_VIDEO_DISINI" -a
```

**Contoh:**
```bash
python dwnld.py "https://youtu.be/dQw4w9WgXcQ" -a
python dwnld.py "https://youtube.com/shorts/EvnSU0e_qL0"
python dwnld.py "https://www.tiktok.com/@username/video/1234567890"
```

---

## 3️⃣ 🔍 Whois/IP Lookup Tool (whois_lookup.py)

Cek informasi detail tentang domain atau IP address, termasuk lokasi, ISP, DNS records, ping test, dan port scanner. Cocok buat analisis jaringan atau sekedar penasaran info website.

### **✨ Fitur:**
 * **IP/Domain Info:** Lokasi geografis, ISP, organization, timezone
 * **DNS Records:** A, AAAA, MX records
 * **Ping Test:** Test koneksi & latency
 * **Port Scanner:** Scan port-port umum (HTTP, HTTPS, SSH, FTP, dll)

### **🚀 Cara Pakai:**

**Basic Lookup (Info IP/Domain):**
```bash
python whois_lookup.py google.com
python whois_lookup.py 8.8.8.8
```

**Dengan Ping Test:**
```bash
python whois_lookup.py github.com --ping
```

**Dengan Port Scan:**
```bash
python whois_lookup.py facebook.com --scan
```

**All-in-One (Semua Test):**
```bash
python whois_lookup.py instagram.com --all
```

**Options:**
- `-p, --ping` : Ping test (4x)
- `-s, --scan` : Scan port umum
- `-d, --dns` : Tampilkan DNS records
- `-a, --all` : Jalankan semua test

---

## 4️⃣ 📱 QR Code Generator & Reader (qrcode_tool.py)

Generate QR code dari text/URL atau decode QR code dari gambar. Support WiFi QR (auto-connect) dan vCard (kontak).

### **✨ Fitur:**
 * **Generate QR:** Dari text, URL, atau data apapun
 * **Read QR:** Decode QR dari foto/screenshot
 * **WiFi QR:** Generate QR untuk auto-connect WiFi
 * **Contact QR:** Generate QR vCard untuk save kontak
 * **Terminal Preview:** Tampil langsung di terminal (ASCII art)

### **🚀 Cara Pakai:**

**Generate QR dari Text/URL:**
```bash
python qrcode_tool.py generate "https://github.com"
python qrcode_tool.py generate "Hello World!" my_qr.png
```

**Read/Decode QR dari Gambar:**
```bash
python qrcode_tool.py read /sdcard/Download/qr_image.jpg
```

**Generate WiFi QR (Auto-Connect):**
```bash
python qrcode_tool.py wifi "RumahKu" "password123" wifi_qr.png
```

**Generate Contact QR (vCard):**
```bash
python qrcode_tool.py contact "John Doe" "081234567890" "john@email.com" contact.png
```

💡 **Tip:** QR WiFi bisa langsung di-scan buat auto-connect tanpa ketik password!

---

## 5️⃣ 📊 File Organizer Otomatis (file_organizer.py)

Auto-organize file di folder Download berdasarkan tipe (Video, Music, Pictures, Documents, dll). Bisa juga hapus file duplikat dan undo organize!

### **✨ Fitur:**
 * **Auto-Categorize:** Sort file ke folder berdasarkan tipe
 * **Duplicate Detection:** Hapus file duplikat (berdasarkan MD5 hash)
 * **Dry Run Mode:** Preview sebelum organize (testing)
 * **Undo Function:** Kembalikan file ke posisi semula
 * **Smart Naming:** Auto-rename jika file sudah ada

### **🚀 Cara Pakai:**

**Organize Download Folder (Default):**
```bash
python file_organizer.py
```

**Preview Dulu (Dry Run):**
```bash
python file_organizer.py --dry-run
```

**Organize + Hapus Duplikat:**
```bash
python file_organizer.py --remove-duplicates
```

**Organize Folder Tertentu:**
```bash
python file_organizer.py /sdcard/DCIM
```

**Undo Organize (Kembalikan ke Semula):**
```bash
python file_organizer.py --undo
```

**Hapus Folder Kosong:**
```bash
python file_organizer.py --clean
```

### **📁 Kategori File:**
- **Videos:** mp4, mkv, avi, mov, webm, dll
- **Music:** mp3, wav, flac, aac, m4a, dll
- **Pictures:** jpg, png, gif, svg, webp, dll
- **Documents:** pdf, docx, xlsx, pptx, txt, dll
- **Archives:** zip, rar, 7z, tar, gz, dll
- **Apps:** apk, xapk
- **Code:** py, js, html, css, java, dll
- **Ebooks:** epub, mobi, azw3, dll
- **Others:** File lainnya yang ga masuk kategori

---

## 🔧 Troubleshooting

### **Error: "ffmpeg is not installed"**
**Solusi:**
```bash
pkg install ffmpeg -y
```

### **Warning: "No supported JavaScript runtime"**
Ini cuma warning, tapi bisa bikin beberapa video ga bisa di-download. Install Deno buat fix:
```bash
pkg install deno -y
```

### **Error: "Permission denied" saat save file**
Pastikan udah jalanin `termux-setup-storage` dan kasih izin akses storage saat diminta.

### **Video berhasil di-download tapi ga ketemu filenya**
File tersimpan di `/storage/emulated/0/Download/` atau `/sdcard/Download/`. Cek file manager HP lo.

### **Error: "Unable to extract video data"**
Kemungkinan:
- Link salah atau video udah dihapus
- Akun/video di-private
- Koneksi internet lo lemot/putus
- Update yt-dlp: `pip install --upgrade yt-dlp`

### **Error QR Code: "No module named 'pyzbar'"**
Install zbar dulu:
```bash
pkg install zbar -y
pip install pyzbar
```

### **QR Reader ga detect QR code**
Pastikan:
- Gambar QR jelas (tidak blur)
- QR code tidak terpotong
- Format gambar didukung (jpg, png)
- Coba crop gambar biar fokus ke QR aja

---

## 📝 Requirements

- **Termux** (Download dari [F-Droid](https://f-droid.org/packages/com.termux/) atau Play Store)
- **Python 3.x** (auto-install via `pkg install python`)
- **FFmpeg** (wajib buat merge video+audio)
- **zbar** (wajib buat QR code reader)
- **yt-dlp** (auto-install via requirements.txt)
- **Pillow** (buat ASCII art & QR code)
- **qrcode** (buat generate QR)
- **pyzbar** (buat decode QR)

---

## 📦 File Structure

```
bototp-main/
├── README.md              # Dokumentasi (file ini)
├── requirements.txt       # Python dependencies
├── ascii_maker.py         # ASCII Art Generator
├── dwnld.py              # Sosmed Video Downloader
├── whois_lookup.py       # Whois/IP Lookup Tool
├── qrcode_tool.py        # QR Code Generator & Reader
└── file_organizer.py     # File Organizer Otomatis
```

---

## 🤝 Kontribusi

Punya ide script keren buat Termux? Pull request aja bos! Atau kalo nemu bug, bikin issue aja.

---

## ⚖️ Disclaimer

Script ini dibuat untuk keperluan edukasi dan personal use. Jangan dipake buat hal-hal ilegal ya (misal: download konten berhak cipta tanpa izin, dll). Gunakan dengan bijak! 

---

*Dibuat untuk seru-seruan & mempermudah hidup di Termux 📱*

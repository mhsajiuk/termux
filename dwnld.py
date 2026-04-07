import os
import argparse
import yt_dlp

def download_media(url, audio_only=False):
    # Cek apakah Termux storage udah disetup, kalau belum simpan di folder saat ini
    download_folder = os.path.expanduser('~/storage/downloads/')
    if not os.path.exists(download_folder):
        download_folder = ''
    
    out_template = os.path.join(download_folder, '%(title)s.%(ext)s')

        # Pengaturan dasar yt-dlp + BYPASS YOUTUBE
    ydl_opts = {
        'outtmpl': out_template,
        'noplaylist': True, 
        
        # JURUS SAKTI: Nyamar jadi aplikasi YouTube di Android biar gak dimintain login
        'extractor_args': {
            'youtube': ['player_client=android,ios']
        },
        
        # Biar gak kelihatan terlalu bar-bar nyedot datanya
        'sleep_interval': 2,
    }

    print("\n" + "="*50)
    print("🚀 ULTIMATE SOSMED DOWNLOADER")
    print("="*50)

    if audio_only:
        print("[*] Mode: 🎵 Audio (MP3)")
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # Kualitas MP3 192kbps
            }],
        })
    else:
        print("[*] Mode: 🎬 Video (Highest Quality)")
        # Cari video mp4 kualitas tertinggi dan gabung dengan audio terbaik
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        })

    print(f"[*] Target URL : {url}")
    print("[*] Memproses  : Tunggu sebentar (tergantung sinyal lo)...\n")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n[+] BOOM! Download Sukses! 🎉")
        print(f"[+] File disimpen di folder Download HP lo.")
    except Exception as e:
        print(f"\n[!] Yah gagal bos. Pastiin linknya bener dan akun gak di-private.")
        print(f"[!] Error Detail: {e}")
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Script buat sedot video/audio dari Sosmed via Termux.")
    parser.add_argument("url", help="Link video (YouTube, TikTok, IG Reels, Twitter, dll)")
    parser.add_argument("-a", "--audio", action="store_true", help="Download suaranya aja (MP3)")
    
    args = parser.parse_args()
    download_media(args.url, args.audio)

if __name__ == "__main__":
    main()

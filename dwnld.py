import os
import re
import argparse
import yt_dlp

def download_media(url, audio_only=False, with_thumbnail=False):
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

        # Fix: sanitize nama file, hapus karakter aneh di awal (titik, spasi, dll)
        'restrictfilenames': False,
    }

    # Hook buat rename file kalau ada titik di depan nama (hidden file bug)
    def fix_hidden_file(d):
        if d['status'] == 'finished':
            filepath = d['filename']
            dirpath = os.path.dirname(filepath)
            basename = os.path.basename(filepath)
            # Hapus titik di awal nama file
            clean_basename = re.sub(r'^\.+', '', basename)
            if clean_basename != basename:
                new_filepath = os.path.join(dirpath, clean_basename)
                os.rename(filepath, new_filepath)

    ydl_opts['progress_hooks'] = [fix_hidden_file]

    print("\n" + "="*50)
    print("🚀 ULTIMATE SOSMED DOWNLOADER")
    print("="*50)

    if with_thumbnail:
        print("[*] Thumbnail: ✅ Aktif (disimpen sebagai .jpg)")
        ydl_opts['writethumbnail'] = True
        ydl_opts.setdefault('postprocessors', []).append(
            {'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'}
        )

    if audio_only:
        print("[*] Mode: 🎵 Audio (MP3)")
        postprocessors = ydl_opts.pop('postprocessors', [])
        postprocessors.insert(0, {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',  # Kualitas MP3 192kbps
        })
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': postprocessors,
        })
    else:
        print("[*] Mode: 🎬 Video (Highest Quality)")
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        })

    print(f"[*] Target URL : {url}")
    print("[*] Memproses  : Tunggu sebentar (tergantung sinyal lo)...\n")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n[+] BOOM! Download Sukses! 🎉")
        if with_thumbnail:
            print(f"[+] Thumbnail juga disimpen sebagai file .jpg.")
        print(f"[+] File disimpen di folder Download HP lo.")
    except Exception as e:
        print(f"\n[!] Yah gagal bos. Pastiin linknya bener dan akun gak di-private.")
        print(f"[!] Error Detail: {e}")
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Script buat sedot video/audio dari Sosmed via Termux.")
    parser.add_argument("url", help="Link video (YouTube, TikTok, IG Reels, Twitter, dll)")
    parser.add_argument("-a", "--audio", action="store_true", help="Download suaranya aja (MP3)")
    parser.add_argument("-t", "--thumbnail", action="store_true", help="Download thumbnail juga (.jpg terpisah)")

    args = parser.parse_args()
    download_media(args.url, args.audio, args.thumbnail)

if __name__ == "__main__":
    main()

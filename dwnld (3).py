import os
import re
import argparse
import yt_dlp

def sanitize_title(title):
    # Hapus titik & spasi di awal judul
    return re.sub(r'^[\.\s]+', '', title)

def download_media(url, audio_only=False, with_thumbnail=False):
    download_folder = os.path.expanduser('~/storage/downloads/')
    if not os.path.exists(download_folder):
        download_folder = ''

    # Pengaturan dasar yt-dlp + BYPASS YOUTUBE
    ydl_opts = {
    'noplaylist': True,

    # Cookies (WAJIB)
    'cookiefile': 'cookies.txt',

    # JS runtime fix
    'js_runtimes': 'node',

    # Anti 429
    'sleep_interval': 3,
    'max_sleep_interval': 6,

    # Retry biar gak gampang gagal
    'retries': 10,
    'fragment_retries': 10,

    # User-Agent biar lebih manusia
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'
    },

    # (opsional, masih boleh dipakai)
    'extractor_args': {
        'youtube': ['player_client=android']
    },
}

        # Biar gak kelihatan terlalu bar-bar nyedot datanya
        'sleep_interval': 2,
    }

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
            'preferredquality': '192',
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
        # Ambil info dulu buat sanitize judul
        with yt_dlp.YoutubeDL({
    'quiet': True,
    'skip_download': True,
    'cookiefile': 'cookies.txt',
    'js_runtimes': 'node'
}) as ydl_info:
            info = ydl_info.extract_info(url, download=False)
            clean_title = sanitize_title(info.get('title', 'video'))

        out_template = os.path.join(download_folder, clean_title + '.%(ext)s')
        ydl_opts['outtmpl'] = out_template

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"\n[+] BOOM! Download Sukses! 🎉")
        if with_thumbnail:
            print(f"[+] Thumbnail juga disimpen sebagai file .jpg.")
        print(f"[+] File: {clean_title}")
        print(f"[+] Disimpen di folder Download HP lo.")
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

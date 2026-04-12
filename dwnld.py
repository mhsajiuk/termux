import os
import re
import argparse
import yt_dlp

def sanitize_title(title):
    return re.sub(r'^[\.\s]+', '', title)

def download_media(url, audio_only=False, with_thumbnail=False):
    download_folder = os.path.expanduser('~/storage/downloads/')
    if not os.path.exists(download_folder):
        download_folder = '.'

    ydl_opts = {
        'noplaylist': True,

        # Cookies (WAJIB kalau kena bot)
        'cookiefile': 'cookies.txt',

        # JS runtime FIX
        'js_runtimes': {
            'node': {}
        },

        # Anti limit
        'sleep_interval': 3,
        'max_sleep_interval': 6,

        # Retry
        'retries': 10,
        'fragment_retries': 10,

        # Header biar lebih legit
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'
        },

        # Output nanti di-set setelah ambil title
    }

    print("\n" + "="*50)
    print("🚀 ULTIMATE SOSMED DOWNLOADER")
    print("="*50)

    if with_thumbnail:
        print("[*] Thumbnail: ✅ Aktif")
        ydl_opts['writethumbnail'] = True
        ydl_opts.setdefault('postprocessors', []).append({
            'key': 'FFmpegThumbnailsConvertor',
            'format': 'jpg'
        })

    if audio_only:
        print("[*] Mode: 🎵 Audio (MP3)")
        postprocessors = ydl_opts.get('postprocessors', [])
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
        print("[*] Mode: 🎬 Video")
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
        })

    print(f"[*] Target URL : {url}")
    print("[*] Memproses...")

    try:
        # Ambil title dulu (pakai config yang sama biar gak kena bot)
        with yt_dlp.YoutubeDL({
            'quiet': True,
            'skip_download': True,
            'cookiefile': 'cookies.txt',
            'js_runtimes': {
                'node': {}
            }
        }) as ydl_info:
            info = ydl_info.extract_info(url, download=False)
            clean_title = sanitize_title(info.get('title', 'video'))

        out_template = os.path.join(download_folder, clean_title + '.%(ext)s')
        ydl_opts['outtmpl'] = out_template

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("\n[+] Download sukses")
        print(f"[+] File: {clean_title}")

    except Exception as e:
        print("\n[!] Gagal")
        print(f"[!] Detail: {e}")

    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("-a", "--audio", action="store_true")
    parser.add_argument("-t", "--thumbnail", action="store_true")

    args = parser.parse_args()
    download_media(args.url, args.audio, args.thumbnail)

if __name__ == "__main__":
    main()

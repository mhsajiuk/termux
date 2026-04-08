#!/usr/bin/env python3
"""
✂️ VIDEO CLIPPER OTOMATIS
Download video YouTube → detect bagian menarik → crop jadi banyak clip → tambah subtitle otomatis
Dioptimalkan untuk Termux Android dengan Whisper model 'small'
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


# ============================================================
# WARNA CLI
# ============================================================
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"

def log(msg, color=C.WHITE, prefix=""):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.DIM}[{ts}]{C.RESET} {color}{prefix}{msg}{C.RESET}")

def log_info(msg):    log(msg, C.CYAN,    "ℹ️  ")
def log_ok(msg):      log(msg, C.GREEN,   "✅ ")
def log_warn(msg):    log(msg, C.YELLOW,  "⚠️  ")
def log_err(msg):     log(msg, C.RED,     "❌ ")
def log_step(msg):    log(msg, C.MAGENTA, "🔧 ")
def log_header(msg):
    w = shutil.get_terminal_size(fallback=(60, 24)).columns
    line = "═" * min(w - 2, 60)
    print(f"\n{C.BLUE}{line}{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}  {msg}{C.RESET}")
    print(f"{C.BLUE}{line}{C.RESET}\n")


# ============================================================
# DEPENDENCY CHECK
# ============================================================
def check_dependencies():
    """Cek semua dependency wajib sebelum jalan"""
    log_header("CEK DEPENDENCY")
    all_ok = True

    # Python packages
    packages = {
        "whisper":  "pip install openai-whisper",
        "yt_dlp":   "pip install yt-dlp",
    }
    for pkg, install_cmd in packages.items():
        try:
            __import__(pkg)
            log_ok(f"Python: {pkg}")
        except ImportError:
            log_err(f"Python: {pkg} belum terinstall → {install_cmd}")
            all_ok = False

    # System tools
    tools = {
        "ffmpeg":  "pkg install ffmpeg -y",
        "ffprobe": "pkg install ffmpeg -y",
    }
    for tool, install_cmd in tools.items():
        if shutil.which(tool):
            log_ok(f"System: {tool}")
        else:
            log_err(f"System: {tool} tidak ditemukan → {install_cmd}")
            all_ok = False

    if not all_ok:
        print()
        log_err("Dependency kurang! Install dulu lalu jalankan lagi.")
        log_info("Install semua sekaligus:")
        print(f"  {C.YELLOW}pip install openai-whisper yt-dlp && pkg install ffmpeg -y{C.RESET}")
        sys.exit(1)

    log_ok("Semua dependency lengkap!")
    return True


# ============================================================
# DOWNLOAD VIDEO
# ============================================================
def download_video(url: str, output_dir: str) -> str:
    """Download video dari YouTube pakai yt-dlp, return path file"""
    import yt_dlp

    log_header("DOWNLOAD VIDEO")
    log_info(f"URL: {url}")

    out_template = os.path.join(output_dir, "%(title).60s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": out_template,
        "merge_output_format": "mp4",
        "quiet": False,
        "no_warnings": False,
        "extractor_args": {
            "youtube": ["player_client=android,ios"]
        },
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }],
    }

    downloaded_file = None

    class MyLogger:
        def debug(self, msg):
            if msg.startswith("[download]") and "%" in msg:
                print(f"\r  {C.CYAN}{msg.strip()}{C.RESET}", end="", flush=True)
        def warning(self, msg): pass
        def error(self, msg): log_err(msg)

    def progress_hook(d):
        nonlocal downloaded_file
        if d["status"] == "finished":
            downloaded_file = d["filename"]
            print()
            log_ok(f"Download selesai: {os.path.basename(d['filename'])}")

    ydl_opts["logger"] = MyLogger()
    ydl_opts["progress_hooks"] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not downloaded_file:
                # Fallback cari file terbaru di folder
                files = sorted(
                    Path(output_dir).glob("*.mp4"),
                    key=lambda f: f.stat().st_mtime,
                    reverse=True
                )
                if files:
                    downloaded_file = str(files[0])

        if not downloaded_file or not os.path.exists(downloaded_file):
            # Coba cari berdasarkan title
            title = info.get("title", "")[:40] if info else ""
            for f in Path(output_dir).glob("*.mp4"):
                downloaded_file = str(f)
                break

        if not downloaded_file:
            log_err("File hasil download tidak ditemukan!")
            sys.exit(1)

        log_ok(f"File: {downloaded_file}")
        return downloaded_file

    except Exception as e:
        log_err(f"Gagal download: {e}")
        sys.exit(1)


# ============================================================
# GET VIDEO DURATION
# ============================================================
def get_duration(video_path: str) -> float:
    """Ambil durasi video dalam detik pakai ffprobe"""
    cmd = (
        f'ffprobe -v error -show_entries format=duration '
        f'-of default=noprint_wrappers=1:nokey=1 "{video_path}"'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        log_err("Tidak bisa baca durasi video!")
        sys.exit(1)


# ============================================================
# TRANSCRIBE DENGAN WHISPER
# ============================================================
def transcribe_video(video_path: str, model_name: str = "small", language: str = None) -> dict:
    """
    Transcribe audio video pakai Whisper.
    Return dict dengan 'segments' berisi list {start, end, text}
    """
    import whisper

    log_header("TRANSKRIPSI AUDIO (WHISPER)")
    log_info(f"Model: {model_name}")
    log_warn("Proses ini bisa memakan waktu cukup lama di HP Android...")
    log_info("Sabar ya, lagi kerja keras nih 💪")

    # Extract audio dulu ke wav (lebih cepat di-proses Whisper)
    audio_path = video_path.replace(".mp4", "_audio.wav")
    log_step("Ekstrak audio dari video...")

    cmd_audio = (
        f'ffmpeg -y -i "{video_path}" '
        f'-vn -acodec pcm_s16le -ar 16000 -ac 1 '
        f'"{audio_path}" -loglevel error'
    )
    result = subprocess.run(cmd_audio, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        log_err(f"Gagal ekstrak audio: {result.stderr}")
        sys.exit(1)
    log_ok("Audio berhasil diekstrak")

    # Load model
    log_step(f"Loading Whisper model '{model_name}'...")
    log_info("(Download model ~244MB kalau belum ada, sekali aja)")
    try:
        model = whisper.load_model(model_name)
        log_ok("Model berhasil dimuat!")
    except Exception as e:
        log_err(f"Gagal load model: {e}")
        sys.exit(1)

    # Transcribe
    log_step("Mulai transkripsi... ini yang paling lama ⏳")
    transcribe_opts = {
        "word_timestamps": True,
        "verbose": False,
        "task": "transcribe",
        "condition_on_previous_text": True,
        "fp16": False,  # Matikan fp16 biar kompatibel di ARM/Android
    }
    if language:
        transcribe_opts["language"] = language

    start_time = time.time()
    try:
        result = model.transcribe(audio_path, **transcribe_opts)
    except Exception as e:
        log_err(f"Gagal transkripsi: {e}")
        sys.exit(1)

    elapsed = time.time() - start_time
    log_ok(f"Transkripsi selesai dalam {elapsed:.0f} detik!")

    # Cleanup audio temp
    try:
        os.remove(audio_path)
    except Exception:
        pass

    # Flatten segments
    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": float(seg["start"]),
            "end":   float(seg["end"]),
            "text":  seg["text"].strip(),
        })

    log_info(f"Total segmen ditemukan: {len(segments)}")
    return {
        "language": result.get("language", "unknown"),
        "segments": segments,
        "full_text": result.get("text", ""),
    }


# ============================================================
# DETECT HIGHLIGHT SEGMENTS
# ============================================================
def detect_highlights(
    transcript: dict,
    video_duration: float,
    min_clip_duration: float = 20.0,
    max_clip_duration: float = 90.0,
    top_n: int = 5,
) -> list:
    """
    Analisis transcript untuk cari bagian paling menarik/penting.
    Strategi scoring:
    1. Kepadatan kata (banyak kata = aktif bicara)
    2. Kalimat mengandung kata kunci penting
    3. Segment beruntun yang saling nyambung
    4. Avoid silence / segment kosong
    """
    log_header("DETEKSI HIGHLIGHT")

    segments = transcript.get("segments", [])
    if not segments:
        log_warn("Tidak ada segmen dari transkripsi, pakai pembagian rata")
        return _fallback_splits(video_duration, min_clip_duration, max_clip_duration, top_n)

    # --- Kata kunci menarik (umum untuk konten YouTube) ---
    KEYWORDS_HIGH = {
        # Bahasa Indonesia
        "penting", "rahasia", "ternyata", "luar biasa", "keren", "wow", "gila",
        "terbaik", "pertama", "akhirnya", "tunggu", "serius", "beneran", "fakta",
        "cara", "tips", "trik", "hack", "mudah", "gratis", "untung", "rugi",
        "bahaya", "wajib", "harus", "jangan", "segera", "perhatikan", "dengarkan",
        # English
        "important", "secret", "incredible", "amazing", "best", "worst", "finally",
        "actually", "seriously", "wait", "listen", "fact", "truth", "never", "always",
        "free", "easy", "simple", "powerful", "must", "need", "critical", "essential",
        "revealed", "exposed", "shocking", "unbelievable", "top", "number one",
    }

    KEYWORDS_MED = {
        # Bahasa Indonesia
        "jadi", "karena", "sehingga", "contoh", "misalnya", "pertanyaan",
        "jawaban", "kenapa", "bagaimana", "siapa", "kapan", "dimana",
        # English
        "because", "therefore", "example", "question", "answer", "why", "how",
        "what", "when", "where", "who", "but", "however", "although",
    }

    # --- Scoring tiap segmen ---
    def score_segment(seg: dict) -> float:
        text = seg["text"].lower()
        words = text.split()
        duration = seg["end"] - seg["start"]

        if duration <= 0:
            return 0.0

        score = 0.0

        # 1. Kepadatan kata (kata per detik) — ideal 2-4 kata/detik
        word_density = len(words) / duration
        if 1.5 <= word_density <= 5.0:
            score += min(word_density, 4.0)

        # 2. Kata kunci tinggi
        high_hits = sum(1 for kw in KEYWORDS_HIGH if kw in text)
        score += high_hits * 3.0

        # 3. Kata kunci sedang
        med_hits = sum(1 for kw in KEYWORDS_MED if kw in text)
        score += med_hits * 1.0

        # 4. Panjang teks (lebih panjang = lebih informatif)
        score += min(len(words) / 10, 5.0)

        # 5. Kalimat tanya/seru (lebih engaging)
        if "?" in text:
            score += 2.0
        if "!" in text:
            score += 1.5

        # Penalti segment terlalu pendek (< 3 detik)
        if duration < 3.0:
            score *= 0.3

        return score

    # Score semua segment
    scored = []
    for i, seg in enumerate(segments):
        s = score_segment(seg)
        scored.append((i, s, seg))

    # --- Gabungkan segment berurutan jadi clip ---
    # Merge segment yang berdekatan sampai durasi target terpenuhi
    def merge_to_clips(start_idx: int, target_min: float, target_max: float):
        """Dari start_idx, gabungkan segmen sampai durasi target"""
        clip_start = segments[start_idx]["start"]
        clip_end = segments[start_idx]["end"]
        clip_texts = [segments[start_idx]["text"]]
        idx = start_idx + 1

        while idx < len(segments):
            seg = segments[idx]
            next_end = seg["end"]
            dur = next_end - clip_start

            if dur > target_max:
                break

            # Gap antara segment max 3 detik, masih oke untuk digabung
            gap = seg["start"] - clip_end
            if gap > 3.0 and (clip_end - clip_start) >= target_min:
                break

            clip_end = next_end
            clip_texts.append(seg["text"])
            idx += 1

        return clip_start, clip_end, " ".join(clip_texts), idx

    # Pilih top-N segment awal sebagai kandidat clip
    sorted_by_score = sorted(scored, key=lambda x: x[1], reverse=True)
    used_ranges = []  # [(start_time, end_time)]
    clips = []

    def overlaps(s, e):
        for us, ue in used_ranges:
            if not (e <= us or s >= ue):
                return True
        return False

    for idx, score, seg in sorted_by_score:
        if len(clips) >= top_n:
            break
        if score <= 0:
            break

        clip_start, clip_end, clip_text, _ = merge_to_clips(
            idx, min_clip_duration, max_clip_duration
        )

        # Clip terlalu pendek? Extend ke belakang
        if clip_end - clip_start < min_clip_duration:
            # Ambil lebih banyak ke depan
            j = idx + 1
            while j < len(segments) and (clip_end - clip_start) < min_clip_duration:
                clip_end = segments[j]["end"]
                clip_text += " " + segments[j]["text"]
                j += 1

        # Pastikan tidak overlap dengan clip yang sudah dipilih
        if overlaps(clip_start, clip_end):
            continue

        # Bulatkan (padding 0.5 detik di awal/akhir biar tidak terpotong)
        clip_start = max(0, clip_start - 0.5)
        clip_end   = min(video_duration, clip_end + 0.5)

        if clip_end - clip_start < 5.0:
            continue  # Skip clip yang terlalu pendek

        clips.append({
            "start":    clip_start,
            "end":      clip_end,
            "duration": clip_end - clip_start,
            "score":    score,
            "text":     clip_text.strip(),
        })
        used_ranges.append((clip_start, clip_end))

    # Sort berdasarkan waktu kemunculan di video
    clips = sorted(clips, key=lambda x: x["start"])

    if not clips:
        log_warn("Tidak ada highlight ditemukan, pakai pembagian rata")
        return _fallback_splits(video_duration, min_clip_duration, max_clip_duration, top_n)

    log_ok(f"Ditemukan {len(clips)} highlight clip!")
    for i, clip in enumerate(clips, 1):
        start_fmt = _fmt_time(clip["start"])
        end_fmt   = _fmt_time(clip["end"])
        log_info(f"  Clip {i}: {start_fmt} → {end_fmt} ({clip['duration']:.0f}s) | score: {clip['score']:.1f}")

    return clips


def _fallback_splits(duration, min_dur, max_dur, n):
    """Fallback: bagi video jadi n bagian rata"""
    target = min(max_dur, max(min_dur, duration / n))
    clips = []
    t = 0.0
    i = 0
    while t < duration and i < n:
        end = min(t + target, duration)
        clips.append({
            "start":    t,
            "end":      end,
            "duration": end - t,
            "score":    0,
            "text":     "",
        })
        t = end
        i += 1
    return clips


def _fmt_time(seconds: float) -> str:
    """Format detik ke MM:SS"""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def _fmt_srt_time(seconds: float) -> str:
    """Format detik ke HH:MM:SS,mmm untuk SRT"""
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ============================================================
# GENERATE SRT SUBTITLE PER CLIP
# ============================================================
def generate_srt(transcript_segments: list, clip_start: float, clip_end: float) -> str:
    """
    Buat konten file .srt untuk satu clip.
    Waktu subtitle di-offset relatif terhadap clip_start.
    """
    srt_lines = []
    counter = 1

    for seg in transcript_segments:
        seg_start = seg["start"]
        seg_end   = seg["end"]

        # Hanya ambil segmen yang ada di dalam range clip
        if seg_end <= clip_start or seg_start >= clip_end:
            continue

        # Clamp ke dalam range clip
        rel_start = max(seg_start, clip_start) - clip_start
        rel_end   = min(seg_end, clip_end)     - clip_start
        text      = seg["text"].strip()

        if not text or rel_end <= rel_start:
            continue

        srt_lines.append(str(counter))
        srt_lines.append(f"{_fmt_srt_time(rel_start)} --> {_fmt_srt_time(rel_end)}")
        srt_lines.append(text)
        srt_lines.append("")
        counter += 1

    return "\n".join(srt_lines)


# ============================================================
# EXPORT CLIP + BURN SUBTITLE
# ============================================================
def export_clip(
    video_path:   str,
    clip:         dict,
    clip_idx:     int,
    srt_content:  str,
    output_dir:   str,
    burn_subtitle: bool = True,
) -> str:
    """
    Potong video sesuai timestamp clip, burn subtitle, simpan ke output_dir.
    Return path file hasil.
    """
    start    = clip["start"]
    duration = clip["duration"]
    safe_start = _fmt_time(start).replace(":", "m") + "s"

    out_name = f"clip_{clip_idx:02d}_{safe_start}.mp4"
    out_path = os.path.join(output_dir, out_name)

    # Simpan SRT sementara
    srt_path = out_path.replace(".mp4", ".srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    log_step(f"Export clip {clip_idx}: {_fmt_time(start)} ({duration:.0f}s)...")

    if burn_subtitle and srt_content.strip():
        # Escape path untuk ffmpeg subtitles filter
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        # Jika path mengandung spasi, wrap dengan quotes di filter
        sub_filter = f"subtitles='{srt_escaped}':force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,Alignment=2'"

        cmd = (
            f'ffmpeg -y '
            f'-ss {start:.3f} '
            f'-i "{video_path}" '
            f'-t {duration:.3f} '
            f'-vf "{sub_filter}" '
            f'-c:v libx264 -preset fast -crf 23 '
            f'-c:a aac -b:a 128k '
            f'-movflags +faststart '
            f'"{out_path}" '
            f'-loglevel error'
        )
    else:
        # Tanpa burn subtitle (subtitle disimpan terpisah sebagai .srt)
        cmd = (
            f'ffmpeg -y '
            f'-ss {start:.3f} '
            f'-i "{video_path}" '
            f'-t {duration:.3f} '
            f'-c:v libx264 -preset fast -crf 23 '
            f'-c:a aac -b:a 128k '
            f'-movflags +faststart '
            f'"{out_path}" '
            f'-loglevel error'
        )

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        log_warn(f"  Burn subtitle gagal, coba tanpa subtitle... ({result.stderr[:80]})")
        # Retry tanpa subtitle
        cmd_fallback = (
            f'ffmpeg -y '
            f'-ss {start:.3f} '
            f'-i "{video_path}" '
            f'-t {duration:.3f} '
            f'-c:v copy -c:a copy '
            f'"{out_path}" '
            f'-loglevel error'
        )
        subprocess.run(cmd_fallback, shell=True)

    if os.path.exists(out_path):
        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        log_ok(f"  Clip {clip_idx} selesai: {out_name} ({size_mb:.1f} MB)")
        return out_path
    else:
        log_err(f"  Clip {clip_idx} gagal dibuat!")
        return None


# ============================================================
# MAIN PIPELINE
# ============================================================
def run_pipeline(args):
    # Setup output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(
        args.output or os.path.expanduser("~/storage/downloads/video_clips"),
        timestamp
    )
    os.makedirs(output_dir, exist_ok=True)
    log_ok(f"Output folder: {output_dir}")

    # ── STEP 1: Dapatkan video ──────────────────────────────
    if args.input.startswith("http://") or args.input.startswith("https://"):
        # Download dari YouTube/sosmed
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = download_video(args.input, tmpdir)
            # Pindahkan ke output_dir agar tidak kehilangan setelah tmpdir dihapus
            dest = os.path.join(output_dir, os.path.basename(video_path))
            shutil.move(video_path, dest)
            video_path = dest
    else:
        # File lokal
        video_path = os.path.abspath(args.input)
        if not os.path.exists(video_path):
            log_err(f"File tidak ditemukan: {video_path}")
            sys.exit(1)
        log_ok(f"Pakai file lokal: {video_path}")

    # ── STEP 2: Durasi ──────────────────────────────────────
    duration = get_duration(video_path)
    log_info(f"Durasi video: {_fmt_time(duration)} ({duration:.0f} detik)")

    if duration < 10:
        log_err("Video terlalu pendek (< 10 detik)!")
        sys.exit(1)

    # ── STEP 3: Transkripsi ─────────────────────────────────
    transcript = transcribe_video(
        video_path,
        model_name=args.model,
        language=args.language if hasattr(args, "language") else None,
    )

    # Simpan transcript lengkap
    transcript_path = os.path.join(output_dir, "transcript.json")
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    log_ok(f"Transcript disimpan: transcript.json")
    log_info(f"Bahasa terdeteksi: {transcript.get('language', '?').upper()}")

    # ── STEP 4: Detect Highlight ────────────────────────────
    clips = detect_highlights(
        transcript,
        duration,
        min_clip_duration=args.min_duration,
        max_clip_duration=args.max_duration,
        top_n=args.clips,
    )

    # ── STEP 5: Export Tiap Clip ────────────────────────────
    log_header("EXPORT CLIP")
    log_info(f"Total clip yang akan dibuat: {len(clips)}")

    results = []
    for i, clip in enumerate(clips, 1):
        # Generate SRT untuk clip ini
        srt_content = generate_srt(
            transcript.get("segments", []),
            clip["start"],
            clip["end"],
        )

        # Export
        out_path = export_clip(
            video_path=video_path,
            clip=clip,
            clip_idx=i,
            srt_content=srt_content,
            output_dir=output_dir,
            burn_subtitle=not args.no_subtitle,
        )

        if out_path:
            results.append({
                "clip": i,
                "file": out_path,
                "start": _fmt_time(clip["start"]),
                "end":   _fmt_time(clip["end"]),
                "duration": f"{clip['duration']:.0f}s",
                "score": clip["score"],
            })

    # ── STEP 6: Hapus video asli jika diminta ───────────────
    if args.keep_original is False:
        try:
            os.remove(video_path)
            log_info("Video asli dihapus (pakai --keep jika ingin disimpan)")
        except Exception:
            pass

    # ── STEP 7: Summary ─────────────────────────────────────
    log_header("SELESAI! 🎉")
    log_ok(f"Berhasil buat {len(results)} clip dari video!")
    log_ok(f"Semua tersimpan di: {output_dir}")
    print()

    for r in results:
        print(f"  {C.CYAN}Clip {r['clip']}{C.RESET}  {r['start']} → {r['end']} ({r['duration']})  →  {C.GREEN}{os.path.basename(r['file'])}{C.RESET}")

    print()

    # Simpan summary ke JSON
    summary = {
        "input":       args.input,
        "model":       args.model,
        "language":    transcript.get("language"),
        "video_duration": f"{duration:.0f}s",
        "clips_created": len(results),
        "output_dir":  output_dir,
        "clips":       results,
        "generated_at": datetime.now().isoformat(),
    }
    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    log_info("Summary disimpan ke summary.json")


# ============================================================
# CLI
# ============================================================
def print_banner():
    print(f"""
{C.BOLD}{C.MAGENTA}
  ╔══════════════════════════════════════════════════╗
  ║         ✂️  VIDEO CLIPPER OTOMATIS  ✂️            ║
  ║   YouTube → Auto Crop + Subtitle  |  Termux      ║
  ╚══════════════════════════════════════════════════╝
{C.RESET}""")

def print_help_extra():
    print(f"""
{C.BOLD}CONTOH PENGGUNAAN:{C.RESET}

  {C.YELLOW}# Download dari YouTube lalu clip otomatis{C.RESET}
  python video_clipper.py "https://youtu.be/dQw4w9WgXcQ"

  {C.YELLOW}# Dari file lokal{C.RESET}
  python video_clipper.py /sdcard/Download/video.mp4

  {C.YELLOW}# Tentukan jumlah clip & durasi{C.RESET}
  python video_clipper.py "URL" --clips 8 --min-duration 30 --max-duration 60

  {C.YELLOW}# Paksa bahasa Indonesia (lebih akurat){C.RESET}
  python video_clipper.py "URL" --language id

  {C.YELLOW}# Tanpa burn subtitle (subtitle disimpan terpisah .srt){C.RESET}
  python video_clipper.py "URL" --no-subtitle

  {C.YELLOW}# Pilih model Whisper (tiny/base/small/medium/large){C.RESET}
  python video_clipper.py "URL" --model medium

  {C.YELLOW}# Simpan ke folder tertentu{C.RESET}
  python video_clipper.py "URL" --output /sdcard/Download/clips

{C.BOLD}CATATAN PENTING:{C.RESET}
  - Model 'small' (default): akurasi bagus, RAM ~500MB, waktu ~2-3x durasi video
  - Model 'medium': lebih akurat, RAM ~1.5GB, waktu ~4-6x durasi video  
  - Model 'large': paling akurat, RAM ~3GB — TIDAK disarankan di HP
  - Pastikan termux-api terinstall: pkg install termux-api -y
""")


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="✂️ Video Clipper Otomatis — Auto crop highlight + subtitle",
        add_help=True,
    )
    parser.add_argument(
        "input",
        help="URL YouTube atau path file video lokal",
    )
    parser.add_argument(
        "--clips", "-n",
        type=int, default=5,
        help="Jumlah clip yang ingin dibuat (default: 5)",
    )
    parser.add_argument(
        "--min-duration",
        type=float, default=20.0,
        help="Durasi minimum tiap clip dalam detik (default: 20)",
    )
    parser.add_argument(
        "--max-duration",
        type=float, default=90.0,
        help="Durasi maksimum tiap clip dalam detik (default: 90)",
    )
    parser.add_argument(
        "--model", "-m",
        default="small",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3", "turbo"],
        help="Model Whisper yang dipakai (default: small)",
    )
    parser.add_argument(
        "--language", "-l",
        default=None,
        help="Kode bahasa audio (contoh: id, en, ja). Default: auto-detect",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Folder output (default: ~/storage/downloads/video_clips/)",
    )
    parser.add_argument(
        "--no-subtitle",
        action="store_true",
        help="Jangan burn subtitle ke video (subtitle tetap disimpan sebagai .srt)",
    )
    parser.add_argument(
        "--keep",
        dest="keep_original",
        action="store_true",
        default=True,
        help="Simpan video asli setelah selesai (default: disimpan)",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Tampilkan contoh penggunaan lengkap",
    )

    # Cek --examples sebelum parse penuh (tidak butuh argumen input)
    if "--examples" in sys.argv:
        print_help_extra()
        return

    args = parser.parse_args()

    # Validasi
    if args.clips < 1 or args.clips > 20:
        log_err("--clips harus antara 1 sampai 20")
        sys.exit(1)
    if args.min_duration < 5:
        log_err("--min-duration minimal 5 detik")
        sys.exit(1)
    if args.max_duration < args.min_duration:
        log_err("--max-duration harus lebih besar dari --min-duration")
        sys.exit(1)

    # Cek dependency
    check_dependencies()

    # Jalankan pipeline
    run_pipeline(args)


if __name__ == "__main__":
    main()

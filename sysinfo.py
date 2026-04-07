#!/usr/bin/env python3
"""
📊 SISTEM INFO DASHBOARD
Tampilkan info lengkap HP/device: CPU, RAM, Storage, Baterai, Jaringan, dan lainnya
Khusus dioptimalkan untuk Termux di Android
"""

import os
import sys
import time
import socket
import platform
import subprocess
import json
import re
import shutil
from datetime import datetime, timedelta
from urllib.request import urlopen
from urllib.error import URLError


# ============================================================
# WARNA & STYLING (ANSI Escape Codes)
# ============================================================
class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Warna Teks
    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    # Warna Cerah
    BBLACK   = "\033[90m"
    BRED     = "\033[91m"
    BGREEN   = "\033[92m"
    BYELLOW  = "\033[93m"
    BBLUE    = "\033[94m"
    BMAGENTA = "\033[95m"
    BCYAN    = "\033[96m"
    BWHITE   = "\033[97m"

C = Color()

def cprint(text, color="", bold=False, end="\n"):
    """Cetak teks berwarna"""
    prefix = C.BOLD if bold else ""
    print(f"{prefix}{color}{text}{C.RESET}", end=end)

def check_color_support():
    """Cek apakah terminal support warna"""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def run_cmd(cmd, timeout=5):
    """Jalankan perintah shell, return output atau None jika gagal"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, Exception):
        return None

def read_file(path):
    """Baca isi file, return None jika tidak ada"""
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except Exception:
        return None

def bytes_to_human(byte_val):
    """Konversi bytes ke format manusia (KB, MB, GB)"""
    try:
        byte_val = float(byte_val)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if byte_val < 1024:
                return f"{byte_val:.1f} {unit}"
            byte_val /= 1024
        return f"{byte_val:.1f} TB"
    except (ValueError, TypeError):
        return "N/A"

def make_bar(percent, width=20, fill='█', empty='░'):
    """Buat progress bar berdasarkan persentase"""
    try:
        percent = max(0, min(100, float(percent)))
        filled = int(width * percent / 100)
        bar = fill * filled + empty * (width - filled)
        return bar
    except (ValueError, TypeError):
        return empty * width

def bar_color(percent):
    """Return warna berdasarkan persentase penggunaan"""
    try:
        p = float(percent)
        if p >= 85:
            return C.BRED
        elif p >= 60:
            return C.BYELLOW
        else:
            return C.BGREEN
    except (ValueError, TypeError):
        return C.BWHITE

def section_header(title, icon=""):
    """Cetak header section yang rapi"""
    term_width = shutil.get_terminal_size(fallback=(60, 24)).columns
    line = "─" * min(term_width - 2, 58)
    print()
    cprint(f"┌{line}┐", C.BBLUE)
    padding = " " * max(0, (min(term_width - 2, 58) - len(title) - len(icon) - 2) // 2)
    cprint(f"│{padding}{icon} {title}{padding}", C.BBLUE, end="")
    cprint("│", C.BBLUE)
    cprint(f"└{line}┘", C.BBLUE)

def info_row(label, value, label_color=C.BCYAN, value_color=C.BWHITE, icon=""):
    """Cetak baris info label: value"""
    label_str = f"  {icon} {label:<22}" if icon else f"  {label:<24}"
    cprint(label_str, label_color, end="")
    cprint(f": {value}", value_color)

def bar_row(label, used, total, unit="", icon=""):
    """Cetak baris dengan progress bar"""
    try:
        percent = (used / total * 100) if total > 0 else 0
        bar = make_bar(percent)
        color = bar_color(percent)
        label_str = f"  {icon} {label:<22}" if icon else f"  {label:<24}"
        cprint(label_str, C.BCYAN, end="")
        cprint(f": [{color}{bar}{C.RESET}] ", end="")
        cprint(f"{percent:.1f}%", color, end="")
        if unit:
            cprint(f"  ({used:.1f}/{total:.1f} {unit})", C.BBLUE)
        else:
            cprint("", C.RESET)
    except Exception:
        info_row(label, "N/A", icon=icon)


# ============================================================
# BANNER
# ============================================================
def print_banner():
    """Cetak banner ASCII art"""
    term_width = shutil.get_terminal_size(fallback=(60, 24)).columns
    now = datetime.now().strftime("%d %b %Y  %H:%M:%S")

    banner_lines = [
        "  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓",
        "  ┃   📊  SISTEM INFO DASHBOARD  📊         ┃",
        "  ┃      Termux Android Edition             ┃",
        "  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛",
    ]

    print()
    for line in banner_lines:
        cprint(line, C.BMAGENTA, bold=True)

    cprint(f"\n  🕐 {now}", C.BBLUE)
    print()


# ============================================================
# 1. INFO PERANGKAT & OS
# ============================================================
def get_device_info():
    """Ambil informasi dasar perangkat"""
    section_header("INFORMASI PERANGKAT", "📱")

    # Hostname
    hostname = socket.gethostname()
    info_row("Hostname", hostname, icon="🏷️ ")

    # Username
    user = os.environ.get("USER", os.environ.get("USERNAME", "termux"))
    info_row("User", user, icon="👤")

    # OS / Kernel
    kernel = run_cmd("uname -r") or platform.release()
    uname_s = run_cmd("uname -s") or platform.system()
    info_row("Kernel", f"{uname_s} {kernel}", icon="🐧")

    # Android version (khusus Termux)
    android_ver = run_cmd("getprop ro.build.version.release")
    if android_ver:
        info_row("Android", f"Android {android_ver}", icon="📲")
    else:
        info_row("OS", platform.system(), icon="💻")

    # Model HP (khusus Android)
    brand = run_cmd("getprop ro.product.brand")
    model = run_cmd("getprop ro.product.model")
    if brand and model:
        info_row("Model HP", f"{brand} {model}", icon="📦")

    # Architecture
    arch = run_cmd("uname -m") or platform.machine()
    info_row("Arsitektur", arch, icon="⚙️ ")

    # Python version
    py_ver = f"Python {sys.version.split()[0]}"
    info_row("Python", py_ver, icon="🐍")

    # Shell
    shell = os.environ.get("SHELL", "bash")
    info_row("Shell", os.path.basename(shell), icon="💬")

    # Termux version
    termux_ver = run_cmd("pkg show termux-tools 2>/dev/null | grep Version | head -1 | awk '{print $2}'")
    if termux_ver:
        info_row("Termux Tools", termux_ver, icon="📦")


# ============================================================
# 2. UPTIME & WAKTU
# ============================================================
def get_uptime_info():
    """Ambil info uptime"""
    section_header("UPTIME", "⏱️")

    # Baca dari /proc/uptime
    uptime_raw = read_file("/proc/uptime")
    if uptime_raw:
        try:
            seconds = float(uptime_raw.split()[0])
            td = timedelta(seconds=int(seconds))
            days = td.days
            hours, rem = divmod(td.seconds, 3600)
            minutes, secs = divmod(rem, 60)

            uptime_str = ""
            if days > 0:
                uptime_str += f"{days}h "
            uptime_str += f"{hours:02d}:{minutes:02d}:{secs:02d}"

            info_row("Uptime Device", uptime_str, icon="🔋")
        except Exception:
            info_row("Uptime", "N/A", icon="⏱️ ")
    else:
        info_row("Uptime", "N/A", icon="⏱️ ")

    # Load average
    loadavg = read_file("/proc/loadavg")
    if loadavg:
        parts = loadavg.split()
        load_str = f"{parts[0]}  {parts[1]}  {parts[2]}  (1m 5m 15m)"
        info_row("Load Average", load_str, icon="📈")

    # Tanggal & waktu
    now = datetime.now()
    info_row("Tanggal", now.strftime("%A, %d %B %Y"), icon="📅")
    info_row("Waktu", now.strftime("%H:%M:%S WIB"), icon="🕐")

    # Timezone
    tz_name = run_cmd("cat /etc/timezone") or run_cmd("date +%Z") or "Unknown"
    info_row("Timezone", tz_name, icon="🌏")


# ============================================================
# 3. CPU INFO
# ============================================================
def get_cpu_info():
    """Ambil info CPU"""
    section_header("CPU / PROSESOR", "🔧")

    # Nama CPU
    cpu_info = read_file("/proc/cpuinfo")
    cpu_name = None
    cpu_cores = 0

    if cpu_info:
        for line in cpu_info.splitlines():
            if "Hardware" in line and not cpu_name:
                cpu_name = line.split(":")[-1].strip()
            elif "model name" in line and not cpu_name:
                cpu_name = line.split(":")[-1].strip()
            elif "Processor" in line and not cpu_name:
                cpu_name = line.split(":")[-1].strip()
            elif line.startswith("processor"):
                cpu_cores += 1

    # Fallback
    if not cpu_name:
        cpu_name = run_cmd("getprop ro.product.cpu.abi") or "Unknown"

    info_row("CPU", cpu_name or "Unknown", icon="🔧")
    info_row("Core Count", f"{max(cpu_cores, 1)} core(s)", icon="⚡")

    # CPU Governor & freq
    gov = read_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    if gov:
        info_row("Governor", gov, icon="🎛️ ")

    cur_freq = read_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
    max_freq = read_file("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")

    if cur_freq:
        try:
            cur_mhz = int(cur_freq) // 1000
            freq_str = f"{cur_mhz} MHz"
            if max_freq:
                max_mhz = int(max_freq) // 1000
                freq_str += f"  /  max {max_mhz} MHz"
            info_row("Frekuensi", freq_str, icon="📡")
        except ValueError:
            pass

    # CPU Usage (pakai /proc/stat — sampling 500ms)
    cpu_usage = _get_cpu_usage()
    if cpu_usage is not None:
        bar = make_bar(cpu_usage)
        color = bar_color(cpu_usage)
        print(f"  {'⚙️  CPU Usage':<24}: [{color}{bar}{C.RESET}] {color}{cpu_usage:.1f}%{C.RESET}")

    # Top proses CPU
    top_proc = run_cmd("top -bn1 2>/dev/null | awk 'NR>7 {print $1,$9,$NF}' | sort -k2 -rn | head -3")
    if top_proc:
        print(f"\n  {C.BCYAN}{'Top Proses (CPU%)':<24}{C.RESET}:")
        for line in top_proc.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                pid, cpu_pct, name = parts[0], parts[1], parts[-1]
                print(f"    {C.BBLUE}{name:<20}{C.RESET} {C.BYELLOW}{cpu_pct}%{C.RESET}  PID:{pid}")

def _get_cpu_usage():
    """Hitung CPU usage dengan sampling 2 titik /proc/stat"""
    def read_stat():
        stat = read_file("/proc/stat")
        if not stat:
            return None
        for line in stat.splitlines():
            if line.startswith("cpu "):
                vals = list(map(int, line.split()[1:]))
                return vals
        return None

    s1 = read_stat()
    if not s1:
        return None
    time.sleep(0.4)
    s2 = read_stat()
    if not s2:
        return None

    try:
        idle1, idle2 = s1[3], s2[3]
        total1 = sum(s1)
        total2 = sum(s2)
        delta_total = total2 - total1
        delta_idle  = idle2 - idle1
        if delta_total == 0:
            return 0.0
        return 100.0 * (delta_total - delta_idle) / delta_total
    except Exception:
        return None


# ============================================================
# 4. RAM / MEMORI
# ============================================================
def get_memory_info():
    """Ambil info RAM dan SWAP"""
    section_header("RAM & MEMORI", "🧠")

    meminfo = read_file("/proc/meminfo")
    if not meminfo:
        cprint("  ⚠️  Info memori tidak tersedia.", C.BYELLOW)
        return

    mem = {}
    for line in meminfo.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            key = parts[0].rstrip(':')
            try:
                val = int(parts[1])  # dalam kB
                mem[key] = val
            except ValueError:
                pass

    # RAM
    total_kb = mem.get("MemTotal", 0)
    avail_kb = mem.get("MemAvailable", 0)
    free_kb  = mem.get("MemFree", 0)
    cached_kb = mem.get("Cached", 0) + mem.get("Buffers", 0)
    used_kb  = total_kb - avail_kb

    total_mb = total_kb / 1024
    used_mb  = used_kb  / 1024
    free_mb  = avail_kb / 1024
    cached_mb = cached_kb / 1024

    if total_mb > 0:
        bar_row("RAM Terpakai", used_mb, total_mb, "MB", icon="🧠")
        info_row("RAM Total", f"{bytes_to_human(total_kb * 1024)}", icon="📊")
        info_row("RAM Dipakai", f"{bytes_to_human(used_kb * 1024)}", icon="📉")
        info_row("RAM Tersedia", f"{bytes_to_human(avail_kb * 1024)}", value_color=C.BGREEN, icon="✅")
        info_row("Cached/Buffer", f"{bytes_to_human(cached_kb * 1024)}", value_color=C.BBLUE, icon="💾")

    # SWAP
    swap_total = mem.get("SwapTotal", 0)
    swap_free  = mem.get("SwapFree", 0)
    swap_used  = swap_total - swap_free

    if swap_total > 0:
        print()
        bar_row("SWAP Terpakai", swap_used / 1024, swap_total / 1024, "MB", icon="💿")
        info_row("SWAP Total", bytes_to_human(swap_total * 1024), icon="📊")
    else:
        print()
        info_row("SWAP", "Tidak aktif", value_color=C.BBLUE, icon="💿")


# ============================================================
# 5. STORAGE / PENYIMPANAN
# ============================================================
def get_storage_info():
    """Ambil info storage internal & Termux"""
    section_header("STORAGE / PENYIMPANAN", "💾")

    paths = [
        ("/storage/emulated/0", "Internal Storage"),
        ("/sdcard",             "SD Card"),
        ("/data/data/com.termux/files", "Termux Home"),
        ("/",                   "Root FS"),
    ]

    printed_any = False
    seen_devices = set()

    for path, label in paths:
        if not os.path.exists(path):
            continue
        try:
            stat = os.statvfs(path)
            block_size = stat.f_frsize
            total_b = stat.f_blocks * block_size
            free_b  = stat.f_bavail * block_size
            used_b  = total_b - free_b

            # Hindari duplikat filesystem
            dev_id = os.stat(path).st_dev
            if dev_id in seen_devices:
                continue
            seen_devices.add(dev_id)

            if total_b == 0:
                continue

            total_gb = total_b / (1024**3)
            used_gb  = used_b  / (1024**3)
            free_gb  = free_b  / (1024**3)
            percent  = (used_b / total_b) * 100

            bar = make_bar(percent)
            color = bar_color(percent)
            print(f"\n  {C.BYELLOW}{label}{C.RESET}")
            print(f"  {'  Penggunaan':<24}: [{color}{bar}{C.RESET}] {color}{percent:.1f}%{C.RESET}")
            print(f"  {'  Total':<24}: {C.BWHITE}{total_gb:.2f} GB{C.RESET}")
            print(f"  {'  Dipakai':<24}: {C.BRED}{used_gb:.2f} GB{C.RESET}")
            print(f"  {'  Tersedia':<24}: {C.BGREEN}{free_gb:.2f} GB{C.RESET}")
            printed_any = True

        except (PermissionError, OSError):
            continue

    if not printed_any:
        # Fallback pakai df
        df_out = run_cmd("df -h /storage/emulated/0 /sdcard / 2>/dev/null | tail -n +2")
        if df_out:
            for line in df_out.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    fs, size, used, avail, pct = parts[0], parts[1], parts[2], parts[3], parts[4]
                    cprint(f"  {fs}: {used}/{size} ({pct})", C.BWHITE)
        else:
            cprint("  ⚠️  Info storage tidak tersedia.", C.BYELLOW)


# ============================================================
# 6. BATERAI
# ============================================================
def get_battery_info():
    """Ambil info baterai"""
    section_header("BATERAI", "🔋")

    # Termux API (paling akurat)
    battery_json = run_cmd("termux-battery-status 2>/dev/null", timeout=6)
    if battery_json:
        try:
            data = json.loads(battery_json)
            level    = data.get("percentage", "N/A")
            status   = data.get("status", "Unknown")
            plugged  = data.get("plugged", "Unknown")
            health   = data.get("health", "Unknown")
            temp     = data.get("temperature", None)

            # Progress bar baterai
            if isinstance(level, (int, float)):
                bar = make_bar(level)
                bcolor = bar_color(level)
                # Baterai: warna terbalik (rendah = merah)
                if level <= 20:
                    bcolor = C.BRED
                elif level <= 50:
                    bcolor = C.BYELLOW
                else:
                    bcolor = C.BGREEN
                print(f"  {'🔋 Level':<24}: [{bcolor}{bar}{C.RESET}] {bcolor}{level}%{C.RESET}")

            status_icon = "🔌" if "CHARGING" in str(status).upper() else "🔋"
            info_row("Status", str(status).replace("_", " ").title(), icon=status_icon)
            info_row("Sumber Daya", str(plugged).replace("_", " ").title(), icon="⚡")
            info_row("Kesehatan", str(health).replace("_", " ").title(), icon="❤️ ")

            if temp is not None:
                temp_color = C.BRED if float(temp) > 40 else C.BGREEN
                info_row("Suhu", f"{temp}°C", value_color=temp_color, icon="🌡️ ")
            return
        except (json.JSONDecodeError, Exception):
            pass

    # Fallback: baca langsung dari /sys
    batt_paths = [
        "/sys/class/power_supply/battery",
        "/sys/class/power_supply/BAT0",
        "/sys/class/power_supply/BAT1",
    ]

    for batt_path in batt_paths:
        if not os.path.exists(batt_path):
            continue

        cap   = read_file(f"{batt_path}/capacity")
        stat  = read_file(f"{batt_path}/status")
        temp  = read_file(f"{batt_path}/temp")
        volt  = read_file(f"{batt_path}/voltage_now")
        tech  = read_file(f"{batt_path}/technology")
        hlth  = read_file(f"{batt_path}/health")

        if cap:
            level = int(cap)
            bar   = make_bar(level)
            if level <= 20:
                bcolor = C.BRED
            elif level <= 50:
                bcolor = C.BYELLOW
            else:
                bcolor = C.BGREEN
            print(f"  {'🔋 Level':<24}: [{bcolor}{bar}{C.RESET}] {bcolor}{level}%{C.RESET}")

        if stat:
            info_row("Status", stat, icon="⚡")
        if hlth:
            info_row("Kesehatan", hlth, icon="❤️ ")
        if tech:
            info_row("Teknologi", tech, icon="🔬")
        if temp:
            try:
                t = float(temp) / 10
                t_color = C.BRED if t > 40 else C.BGREEN
                info_row("Suhu", f"{t:.1f}°C", value_color=t_color, icon="🌡️ ")
            except ValueError:
                pass
        if volt:
            try:
                v = float(volt) / 1000000
                info_row("Voltase", f"{v:.3f} V", icon="⚡")
            except ValueError:
                pass
        return

    cprint("  ⚠️  termux-battery-status tidak tersedia.", C.BYELLOW)
    cprint("  💡 Install dengan: pkg install termux-api", C.BBLUE)


# ============================================================
# 7. JARINGAN
# ============================================================
def get_network_info():
    """Ambil info jaringan"""
    section_header("JARINGAN", "🌐")

    # IP lokal per interface
    ip_out = run_cmd("ip addr show 2>/dev/null") or run_cmd("ifconfig 2>/dev/null")
    interfaces = {}

    if ip_out:
        cur_iface = None
        for line in ip_out.splitlines():
            # Interface line
            iface_match = re.match(r'^\d+:\s+(\S+):', line)
            if iface_match:
                cur_iface = iface_match.group(1).rstrip(':')
                continue
            # IPv4
            ip4_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', line)
            if ip4_match and cur_iface and cur_iface not in ('lo',):
                interfaces.setdefault(cur_iface, {})['ipv4'] = ip4_match.group(1)
            # IPv6
            ip6_match = re.search(r'inet6\s+([0-9a-f:]+)', line)
            if ip6_match and cur_iface and cur_iface not in ('lo',):
                ip6 = ip6_match.group(1)
                if not ip6.startswith('fe80'):  # skip link-local
                    interfaces.setdefault(cur_iface, {})['ipv6'] = ip6

    if interfaces:
        for iface, addrs in interfaces.items():
            ipv4 = addrs.get('ipv4', '-')
            ipv6 = addrs.get('ipv6', '-')
            icon = "📶" if "wlan" in iface.lower() or "wifi" in iface.lower() else "📡"
            info_row(f"Interface [{iface}]", ipv4, icon=icon)
            if ipv6 != '-':
                info_row(f"  IPv6", ipv6, value_color=C.BBLUE, icon="  ")
    else:
        info_row("IP Lokal", "Tidak terhubung", value_color=C.BRED, icon="❌")

    # IP Publik
    print()
    cprint("  🌍 Mencari IP Publik...", C.BBLUE, end="\r")
    pub_ip = None
    pub_info = None

    for api_url in [
        "http://ip-api.com/json/?fields=status,query,country,city,isp,org,timezone",
        "http://ipinfo.io/json",
    ]:
        try:
            with urlopen(api_url, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "success" or "ip" in data or "query" in data:
                    pub_ip = data.get("query") or data.get("ip")
                    pub_info = data
                    break
        except Exception:
            continue

    if pub_ip:
        print(" " * 40, end="\r")  # clear loading text
        info_row("IP Publik", pub_ip, value_color=C.BMAGENTA, icon="🌍")
        if pub_info:
            city    = pub_info.get("city", "")
            country = pub_info.get("country", "")
            isp     = pub_info.get("isp", pub_info.get("org", ""))
            tz      = pub_info.get("timezone", "")
            if city or country:
                info_row("Lokasi", f"{city}, {country}", icon="📍")
            if isp:
                info_row("ISP / Provider", isp[:40], icon="🏢")
            if tz:
                info_row("Timezone", tz, icon="🌏")
    else:
        print(" " * 40, end="\r")
        info_row("IP Publik", "Tidak dapat diambil (offline?)", value_color=C.BRED, icon="❌")

    # DNS
    dns_servers = []
    resolv = read_file("/etc/resolv.conf")
    if resolv:
        for line in resolv.splitlines():
            if line.startswith("nameserver"):
                parts = line.split()
                if len(parts) >= 2:
                    dns_servers.append(parts[1])

    if dns_servers:
        info_row("DNS Server", ", ".join(dns_servers[:3]), icon="🔗")

    # WiFi SSID (via termux-wifi-connectioninfo atau iw)
    wifi_json = run_cmd("termux-wifi-connectioninfo 2>/dev/null", timeout=5)
    if wifi_json:
        try:
            wdata = json.loads(wifi_json)
            ssid  = wdata.get("ssid", "")
            freq  = wdata.get("frequency_mhz", "")
            speed = wdata.get("link_speed_mbps", "")
            rssi  = wdata.get("rssi", "")
            if ssid and ssid != "<unknown ssid>":
                print()
                info_row("WiFi SSID", ssid, icon="📶")
                if freq:
                    info_row("Frekuensi", f"{freq} MHz", icon="📡")
                if speed:
                    info_row("Link Speed", f"{speed} Mbps", icon="⚡")
                if rssi:
                    rssi_int = int(rssi)
                    if rssi_int > -60:
                        sig = "Bagus 🟢"
                    elif rssi_int > -75:
                        sig = "Sedang 🟡"
                    else:
                        sig = "Lemah 🔴"
                    info_row("Sinyal (RSSI)", f"{rssi} dBm  {sig}", icon="📊")
        except Exception:
            pass


# ============================================================
# 8. PING TEST
# ============================================================
def get_ping_info():
    """Ping test ke beberapa server"""
    section_header("PING TEST", "📡")

    targets = [
        ("Google DNS",      "8.8.8.8"),
        ("Cloudflare DNS",  "1.1.1.1"),
        ("Google.com",      "google.com"),
    ]

    for label, host in targets:
        result = run_cmd(f"ping -c 2 -W 3 {host} 2>/dev/null", timeout=8)
        if result:
            # Ambil avg ping
            match = re.search(r'min/avg/max.*?=\s*[\d.]+/([\d.]+)/', result)
            if match:
                avg_ms = float(match.group(1))
                if avg_ms < 50:
                    ping_color = C.BGREEN
                elif avg_ms < 150:
                    ping_color = C.BYELLOW
                else:
                    ping_color = C.BRED
                info_row(label, f"{ping_color}{avg_ms:.1f} ms{C.RESET}", icon="📡")
            else:
                info_row(label, "Online (timeout unknown)", icon="📡")
        else:
            info_row(label, f"{C.BRED}Timeout / Offline{C.RESET}", icon="❌")


# ============================================================
# 9. PROSES & APLIKASI
# ============================================================
def get_process_info():
    """Info proses yang sedang berjalan"""
    section_header("PROSES AKTIF", "⚙️")

    # Total proses
    procs = run_cmd("ls /proc | grep '^[0-9]' | wc -l")
    if procs:
        info_row("Total Proses", procs, icon="⚙️ ")

    # Top 5 proses berdasarkan memory
    print(f"\n  {C.BCYAN}Top 5 Proses (Memory):{C.RESET}")
    top_mem = run_cmd("top -bn1 2>/dev/null | awk 'NR>7 {print $1,$10,$NF}' | sort -k2 -rn | head -5")
    if top_mem:
        print(f"  {'PID':<8} {'MEM%':<8} {'Nama'}")
        print(f"  {'─'*8} {'─'*8} {'─'*20}")
        for line in top_mem.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                pid, mem_pct, name = parts[0], parts[1], parts[-1]
                mem_f = float(mem_pct) if mem_pct.replace('.','').isdigit() else 0
                c = C.BRED if mem_f > 10 else (C.BYELLOW if mem_f > 5 else C.BWHITE)
                print(f"  {C.BBLUE}{pid:<8}{C.RESET} {c}{mem_pct:<8}{C.RESET} {name}")


# ============================================================
# 10. RINGKASAN / SUMMARY
# ============================================================
def print_summary():
    """Cetak ringkasan singkat di bagian bawah"""
    section_header("RINGKASAN", "📋")

    # RAM
    meminfo = read_file("/proc/meminfo")
    if meminfo:
        mem = {}
        for line in meminfo.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                try:
                    mem[parts[0].rstrip(':')] = int(parts[1])
                except ValueError:
                    pass
        total_kb = mem.get("MemTotal", 0)
        avail_kb = mem.get("MemAvailable", 0)
        if total_kb > 0:
            ram_pct = (total_kb - avail_kb) / total_kb * 100
            rcolor = bar_color(ram_pct)
            print(f"  🧠 RAM     : {rcolor}{ram_pct:.0f}%{C.RESET} terpakai  ({bytes_to_human(avail_kb*1024)} tersedia)")

    # Storage internal
    try:
        for path in ["/storage/emulated/0", "/sdcard", "/"]:
            if os.path.exists(path):
                s = os.statvfs(path)
                total = s.f_blocks * s.f_frsize
                avail = s.f_bavail * s.f_frsize
                if total > 0:
                    pct = (total - avail) / total * 100
                    sc = bar_color(pct)
                    print(f"  💾 Storage : {sc}{pct:.0f}%{C.RESET} terpakai  ({bytes_to_human(avail)} tersedia)")
                    break
    except Exception:
        pass

    # CPU usage
    cpu_u = _get_cpu_usage()
    if cpu_u is not None:
        cc = bar_color(cpu_u)
        print(f"  ⚙️  CPU     : {cc}{cpu_u:.0f}%{C.RESET} terpakai")

    # Baterai ringkas
    bat_json = run_cmd("termux-battery-status 2>/dev/null", timeout=5)
    if bat_json:
        try:
            bd = json.loads(bat_json)
            lvl = bd.get("percentage", "?")
            sta = bd.get("status", "")
            icon = "🔌" if "CHARG" in str(sta).upper() else "🔋"
            bc = C.BGREEN if lvl >= 50 else (C.BYELLOW if lvl >= 20 else C.BRED)
            print(f"  {icon} Baterai  : {bc}{lvl}%{C.RESET}  ({sta})")
        except Exception:
            pass

    print()
    term_width = shutil.get_terminal_size(fallback=(60, 24)).columns
    line = "═" * min(term_width - 2, 58)
    cprint(f"\n  {line}", C.BMAGENTA)
    cprint(f"  ✅ Scan selesai: {datetime.now().strftime('%H:%M:%S')}", C.BGREEN)
    cprint(f"  {line}\n", C.BMAGENTA)


# ============================================================
# MAIN
# ============================================================
def parse_args():
    """Parse argumen CLI sederhana tanpa argparse"""
    args = sys.argv[1:]
    options = {
        "quick":   False,
        "network": False,
        "battery": False,
        "storage": False,
        "cpu":     False,
        "ping":    False,
        "all":     False,
    }

    for a in args:
        a = a.lower().lstrip("-")
        if a in options:
            options[a] = True

    # Jika tidak ada flag spesifik, tampilkan semua
    if not any(options.values()):
        options["all"] = True

    return options


def print_help():
    print("""
╔══════════════════════════════════════════════════════╗
║          📊 SISTEM INFO DASHBOARD - HELP             ║
╚══════════════════════════════════════════════════════╝

PENGGUNAAN:
  python sysinfo.py [opsi]

OPSI:
  (tanpa opsi)    Tampilkan semua info (default)
  --all           Tampilkan semua info
  --quick         Tampilkan ringkasan singkat saja
  --cpu           Info CPU & penggunaan
  --network       Info jaringan & IP
  --battery       Info baterai
  --storage       Info penyimpanan
  --ping          Ping test ke server umum

CONTOH:
  python sysinfo.py
  python sysinfo.py --quick
  python sysinfo.py --network --ping
  python sysinfo.py --cpu --battery

CATATAN:
  - Install Termux:API untuk info baterai & WiFi lebih lengkap:
    pkg install termux-api
  - Beberapa info memerlukan izin storage (termux-setup-storage)
""")


def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("-h", "--help", "help"):
        print_help()
        return

    opts = parse_args()

    print_banner()

    if opts["quick"]:
        print_summary()
        return

    if opts["all"]:
        get_device_info()
        get_uptime_info()
        get_cpu_info()
        get_memory_info()
        get_storage_info()
        get_battery_info()
        get_network_info()
        get_ping_info()
        get_process_info()
        print_summary()
        return

    # Mode selektif
    if opts["cpu"]:
        get_cpu_info()
    if opts["network"]:
        get_network_info()
    if opts["battery"]:
        get_battery_info()
    if opts["storage"]:
        get_storage_info()
    if opts["ping"]:
        get_ping_info()

    print()


if __name__ == "__main__":
    main()

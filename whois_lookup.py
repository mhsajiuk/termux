#!/usr/bin/env python3
"""
🔍 WHOIS/IP LOOKUP TOOL
Cek info domain, IP address, ping test, dan port scanner
"""

import sys
import socket
import subprocess
import json
import re
from urllib.request import urlopen
from urllib.error import URLError

def print_banner():
    banner = """
==================================================
🔍 WHOIS/IP LOOKUP TOOL
==================================================
"""
    print(banner)

def get_ip_info(target):
    """Dapatkan info IP menggunakan ip-api.com (gratis, no API key)"""
    try:
        print(f"[*] Mengambil info untuk: {target}")
        
        # Cek apakah target adalah domain atau IP
        try:
            ip = socket.gethostbyname(target)
            if target != ip:
                print(f"[+] Domain resolved ke IP: {ip}")
        except socket.gaierror:
            ip = target
        
        # Ambil data dari API
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if data.get('status') == 'fail':
            print(f"[!] Error: {data.get('message', 'Unknown error')}")
            return None
        
        return data, ip
        
    except URLError as e:
        print(f"[!] Error koneksi: {e}")
        return None
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def display_ip_info(data, original_ip):
    """Tampilkan info IP dengan format rapi"""
    print("\n" + "="*50)
    print("📍 INFORMASI LOKASI & JARINGAN")
    print("="*50)
    
    info = [
        ("IP Address", data.get('query', original_ip)),
        ("ISP/Provider", data.get('isp', 'N/A')),
        ("Organization", data.get('org', 'N/A')),
        ("AS Number", data.get('as', 'N/A')),
        ("Country", f"{data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})"),
        ("Region", f"{data.get('regionName', 'N/A')} ({data.get('region', 'N/A')})"),
        ("City", data.get('city', 'N/A')),
        ("ZIP Code", data.get('zip', 'N/A')),
        ("Timezone", data.get('timezone', 'N/A')),
        ("Coordinates", f"{data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}"),
    ]
    
    for label, value in info:
        print(f"[+] {label:15} : {value}")
    
    print("="*50)

def ping_test(target, count=4):
    """Ping test ke target"""
    print(f"\n🏓 PING TEST ({count}x)")
    print("="*50)
    
    try:
        # Termux pakai Linux command
        result = subprocess.run(
            ['ping', '-c', str(count), target],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        output = result.stdout
        
        # Parse hasil ping
        if "bytes from" in output:
            print(output)
            
            # Extract statistik
            stats = re.search(r'(\d+) packets transmitted, (\d+) received, ([\d.]+)% packet loss, time ([\d]+)ms', output)
            if stats:
                transmitted, received, loss, time = stats.groups()
                print(f"\n[+] Statistik:")
                print(f"    Transmitted : {transmitted} packets")
                print(f"    Received    : {received} packets")
                print(f"    Packet Loss : {loss}%")
                print(f"    Total Time  : {time}ms")
        else:
            print("[!] Ping gagal - Host unreachable atau timeout")
            
    except subprocess.TimeoutExpired:
        print("[!] Ping timeout (>15 detik)")
    except FileNotFoundError:
        print("[!] Perintah 'ping' tidak ditemukan")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    print("="*50)

def port_scanner(target, ports=[21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080]):
    """Scan port-port umum"""
    print(f"\n🔌 PORT SCANNER (Common Ports)")
    print("="*50)
    print(f"[*] Scanning {target}...")
    
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        print("[!] Tidak bisa resolve hostname")
        return
    
    open_ports = []
    closed_ports = []
    
    port_names = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
        443: "HTTPS", 3306: "MySQL", 3389: "RDP", 8080: "HTTP-Alt"
    }
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            service = port_names.get(port, "Unknown")
            open_ports.append((port, service))
            print(f"[+] Port {port:5} ({service:10}) : OPEN ✓")
        else:
            closed_ports.append(port)
        
        sock.close()
    
    print("\n" + "-"*50)
    print(f"[+] Total Open Ports  : {len(open_ports)}")
    print(f"[+] Total Closed Ports: {len(closed_ports)}")
    print("="*50)

def get_dns_records(domain):
    """Dapatkan DNS records"""
    print(f"\n🌐 DNS RECORDS")
    print("="*50)
    
    try:
        # A Record (IPv4)
        try:
            ip = socket.gethostbyname(domain)
            print(f"[+] A Record (IPv4)  : {ip}")
        except:
            print("[!] A Record tidak ditemukan")
        
        # IPv6 (AAAA Record)
        try:
            result = socket.getaddrinfo(domain, None, socket.AF_INET6)
            ipv6 = result[0][4][0]
            print(f"[+] AAAA Record (IPv6): {ipv6}")
        except:
            print("[!] AAAA Record tidak ditemukan")
        
        # MX Records (via nslookup/dig jika tersedia)
        try:
            result = subprocess.run(
                ['nslookup', '-type=mx', domain],
                capture_output=True,
                text=True,
                timeout=5
            )
            mx_records = re.findall(r'mail exchanger = (.+)', result.stdout)
            if mx_records:
                print(f"[+] MX Records       :")
                for mx in mx_records:
                    print(f"                       {mx}")
            else:
                print("[!] MX Records tidak ditemukan")
        except:
            print("[!] MX Records (install 'bind-tools' untuk detail)")
            
    except Exception as e:
        print(f"[!] Error mendapatkan DNS records: {e}")
    
    print("="*50)

def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print("📖 Cara Pakai:")
        print("   python whois_lookup.py <domain/ip> [options]")
        print("\nOptions:")
        print("   -p, --ping       : Jalankan ping test")
        print("   -s, --scan       : Scan port umum")
        print("   -d, --dns        : Tampilkan DNS records")
        print("   -a, --all        : Jalankan semua test")
        print("\nContoh:")
        print("   python whois_lookup.py google.com")
        print("   python whois_lookup.py 8.8.8.8 --ping")
        print("   python whois_lookup.py github.com -a")
        print("   python whois_lookup.py facebook.com --scan")
        print("="*50)
        sys.exit(1)
    
    target = sys.argv[1]
    options = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Validasi input
    if not re.match(r'^[a-zA-Z0-9.-]+$', target):
        print("[!] Input tidak valid. Gunakan domain atau IP address.")
        sys.exit(1)
    
    # Dapatkan info IP/Domain
    result = get_ip_info(target)
    
    if result:
        data, ip = result
        display_ip_info(data, ip)
    else:
        print("[!] Tidak bisa mendapatkan informasi. Lanjut ke test lainnya...")
        ip = target
    
    # Jalankan test tambahan berdasarkan options
    run_all = '-a' in options or '--all' in options
    
    if run_all or '-d' in options or '--dns' in options:
        get_dns_records(target)
    
    if run_all or '-p' in options or '--ping' in options:
        ping_test(ip)
    
    if run_all or '-s' in options or '--scan' in options:
        port_scanner(ip)
    
    print("\n✅ Selesai!")
    print("="*50)

if __name__ == "__main__":
    main()

import os
import re
import sys
import time
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
TUNNEL_FILE = os.path.join(DATA_DIR, 'public_tunnel.txt')
CLOUDFLARED_BIN = os.path.join(BASE_DIR, 'scripts', 'cloudflared.exe')

def run_tunnel():
    if not os.path.exists(CLOUDFLARED_BIN):
        print(f"Error: {CLOUDFLARED_BIN} not found", flush=True)
        return

    cmd = [CLOUDFLARED_BIN, 'tunnel', '--url', 'http://127.0.0.1:5000']
    print(f"Starting tunnel: {' '.join(cmd)}", flush=True)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding='utf-8',
        errors='replace'
    )

    url_found = False
    url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')

    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        if not line:
            continue
        print(f"[cf] {line}", flush=True)
        
        match = url_pattern.search(line)
        if match and not url_found:
            public_url = match.group(0)
            url_found = True
            
            # Write clean direct URL for website, QR codes and WhatsApp
            with open(TUNNEL_FILE, 'w', encoding='utf-8') as f:
                f.write(public_url.strip())

            print(f"\n==========================================", flush=True)
            print(f"DIRECT CLEAN LIVE URL READY: {public_url}", flush=True)
            print(f"==========================================\n", flush=True)

    proc.wait()
    print("Tunnel process terminated.", flush=True)

if __name__ == '__main__':
    while True:
        try:
            run_tunnel()
        except Exception as e:
            print(f"Tunnel exception: {e}", flush=True)
        time.sleep(3)

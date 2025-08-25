import subprocess
import re
import threading
import shutil
import time

def cloudflare_tunnel(port):
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    url = None
    def reader():
        nonlocal url
        for line in proc.stdout:
            m = re.search(r"https://[0-9a-zA-Z\-]+\.trycloudflare\.com", line)
            if m:
                url = m.group(0)
                break
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    while url is None:
        pass
    return url, proc

def localtunnel(port, subdomain="", max_retries=3):
    if not shutil.which("lt"):
        raise Exception("localtunnel command 'lt' not found. Please install it with: npm install -g localtunnel")
    
    for attempt in range(max_retries):
        cmd = ["lt", "--port", str(port)]
        if subdomain:
            cmd.extend(["--subdomain", subdomain])
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        url = None
        error_detected = False
        
        def reader():
            nonlocal url, error_detected
            for line in proc.stdout:
                if "your url is:" in line.lower():
                    m = re.search(r"https://[0-9a-zA-Z\-]+\.loca\.lt", line)
                    if m:
                        url = m.group(0)
                        break
                elif any(error in line.lower() for error in ["error:", "connection refused", "throw err"]):
                    error_detected = True
                    break
        
        t = threading.Thread(target=reader, daemon=True)
        t.start()
        
        timeout = 15
        start_time = time.time()
        while url is None and not error_detected and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if url is not None:
            return url, proc
        
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        
        if attempt < max_retries - 1:
            time.sleep(1)
    
    raise Exception(f"Failed to establish localtunnel after {max_retries} attempts. Please check your network connection and firewall settings.")

def tunnel(port, tunnel_type="cloudflare", subdomain=""):
    if tunnel_type.lower() == "cloudflare":
        return cloudflare_tunnel(port)
    elif tunnel_type.lower() == "localtunnel":
        return localtunnel(port, subdomain)
    else:
        raise ValueError("Invalid tunnel type. Please use 'cloudflare' or 'localtunnel'")
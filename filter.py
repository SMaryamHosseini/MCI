import requests
import socket
import ssl
import re
import time

SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

TIMEOUT = 2

# ---------- extract IP ----------
def extract_ips(text):
    return re.findall(r'@([\d\.]+):', text)

# ---------- TCP test ----------
def tcp_check(ip, port=443):
    try:
        s = socket.socket()
        s.settimeout(TIMEOUT)
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

# ---------- TLS handshake test (strong signal) ----------
def tls_check(ip, sni="www.google.com"):
    try:
        ctx = ssl.create_default_context()
        s = socket.create_connection((ip, 443), timeout=TIMEOUT)
        ssl_sock = ctx.wrap_socket(s, server_hostname=sni)
        ssl_sock.close()
        return True
    except:
        return False

# ---------- latency test ----------
def latency(ip):
    try:
        start = time.time()
        s = socket.create_connection((ip, 443), timeout=TIMEOUT)
        s.close()
        return (time.time() - start) * 1000
    except:
        return 9999

reachable = []
dead = []

for sub in SUBS:
    print("FETCH:", sub)

    try:
        raw = requests.get(sub, timeout=20).text
    except Exception as e:
        print("SUB ERROR:", e)
        continue

    ips = list(set(extract_ips(raw)))
    print("TOTAL IPS:", len(ips))

    for i, ip in enumerate(ips):
        print(f"{i+1}/{len(ips)} testing {ip}")

        # step 1: TCP
        if not tcp_check(ip):
            dead.append(ip)
            continue

        # step 2: TLS (important for CDN reality)
        if not tls_check(ip):
            dead.append(ip)
            continue

        # step 3: latency score
        ping = latency(ip)

        reachable.append((ip, ping))

# remove duplicates
reachable = list(set(reachable))
reachable.sort(key=lambda x: x[1])

# ---------- save ----------
with open("mci_reachable.txt", "w") as f:
    for ip, ping in reachable:
        f.write(f"{ip} | {int(ping)}ms\n")

with open("dead.txt", "w") as f:
    for ip in dead:
        f.write(ip + "\n")

print("DONE")
print("REACHABLE:", len(reachable))
print("DEAD:", len(dead))

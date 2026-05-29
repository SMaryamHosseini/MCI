import requests
import base64
import re
import socket

SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

CDN = ["23.211","2.16","184.86","104.66","23.58","172.225","104.80","23.210","23.208","23.42"]

TIMEOUT = 1.5

def decode_base64(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return ""

def extract_ip(line):
    m = re.search(r'@([\d\.]+):', line)
    return m.group(1) if m else None

def tcp_check(ip):
    try:
        s = socket.create_connection((ip, 443), timeout=TIMEOUT)
        s.close()
        return True
    except:
        return False

good = []

for url in SUBS:
    print("FETCH:", url)

    raw = requests.get(url, timeout=20).text
    decoded = decode_base64(raw)

    lines = decoded.splitlines()

    print("LINES:", len(lines))

    for i, line in enumerate(lines):
        if "vless://" not in line:
            continue

        ip = extract_ip(line)
        if not ip:
            continue

        # CDN filter
        if not any(ip.startswith(c) for c in CDN):
            continue

        # optional real check (this is what made old version slow)
        if not tcp_check(ip):
            continue

        good.append(line)

good = list(set(good))

with open("mci.txt", "w") as f:
    f.write("\n".join(good))

print("DONE")
print("GOOD:", len(good))

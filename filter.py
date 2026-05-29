import requests
import socket
import ssl
import re
import base64
import time

SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

TIMEOUT = 2

# ---------------- decode ----------------
def decode(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return text

# ---------------- extract hosts ----------------
def extract_hosts(text):
    return re.findall(r'@([\w\.\-]+):', text)

# ---------------- TCP check ----------------
def tcp_check(ip):
    try:
        s = socket.socket()
        s.settimeout(TIMEOUT)
        s.connect((ip, 443))
        s.close()
        return True
    except:
        return False

# ---------------- TLS check with SNI ----------------
def tls_check(ip, sni):
    try:
        ctx = ssl.create_default_context()
        s = socket.create_connection((ip, 443), timeout=TIMEOUT)
        ssl_sock = ctx.wrap_socket(s, server_hostname=sni)
        ssl_sock.close()
        return True
    except:
        return False

# ---------------- latency ----------------
def latency(ip):
    try:
        start = time.time()
        s = socket.create_connection((ip, 443), timeout=TIMEOUT)
        s.close()
        return (time.time() - start) * 1000
    except:
        return 9999

# ---------------- scoring ----------------
def score(ip, sni):
    if not tcp_check(ip):
        return -1
    if not tls_check(ip, sni):
        return -1
    return latency(ip)

mci_good = []
ir_good = []
dead = []

for sub in SUBS:
    print("FETCH:", sub)

    raw = requests.get(sub, timeout=20).text
    decoded = decode(raw)

    hosts = list(set(extract_hosts(decoded)))

    print("TOTAL HOSTS:", len(hosts))

    for i, ip in enumerate(hosts):

        print(f"{i+1}/{len(hosts)} testing {ip}")

        # ---------------- MCI simulation ----------------
        mci_score = score(ip, "www.google.com")

        # ---------------- Irancell simulation ----------------
        ir_score = score(ip, "www.cloudflare.com")

        if mci_score == -1 and ir_score == -1:
            dead.append(ip)
            continue

        # MCI bucket
        if mci_score != -1 and mci_score < 400:
            mci_good.append((ip, mci_score))

        # IR bucket
        if ir_score != -1 and ir_score < 400:
            ir_good.append((ip, ir_score))

# ---------------- deduplicate ----------------
mci_good = sorted(list(set(mci_good)), key=lambda x: x[1])
ir_good = sorted(list(set(ir_good)), key=lambda x: x[1])

# ---------------- save ----------------
with open("mci.txt", "w") as f:
    for ip, sc in mci_good:
        f.write(f"{ip} | {int(sc)}ms\n")

with open("irancell.txt", "w") as f:
    for ip, sc in ir_good:
        f.write(f"{ip} | {int(sc)}ms\n")

with open("dead.txt", "w") as f:
    for ip in dead:
        f.write(ip + "\n")

print("DONE")
print("MCI GOOD:", len(mci_good))
print("IRANCELL GOOD:", len(ir_good))
print("DEAD:", len(dead))

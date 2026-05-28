import socket
import ipaddress
import concurrent.futures
import requests
from urllib.parse import urlparse

# =========================
# 1. YOUR SUB LINK
# =========================
SUB_URL = "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt"


# =========================
# 2. MCI / CDN RANGE LIST
# (همونی که دادی)
# =========================
CDN_IPS = [
    "23.211.53.248","2.16.53.35","184.86.2.78","104.66.72.213",
    "23.58.201.211","2.22.0.41","2.21.200.81","104.66.76.103",
    "95.100.183.211","92.123.122.13","23.207.120.215","104.66.125.77",
    # ... ادامه لیست خودت (می‌تونی کامل بزاری)
]

CDN_SET = set(CDN_IPS)


# =========================
# 3. DOWNLOAD SUB
# =========================
def get_sub():
    r = requests.get(SUB_URL, timeout=10)
    return r.text.splitlines()


# =========================
# 4. EXTRACT HOST/IP FROM VLESS
# =========================
def extract_host(vless):
    try:
        return urlparse(vless).hostname
    except:
        return None


# =========================
# 5. CHECK IF MATCH CDN LIST
# =========================
def is_in_list(ip):
    return ip in CDN_SET


# =========================
# 6. REAL TCP TEST (NO PING)
# =========================
def tcp_test(ip, port=443):
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False


# =========================
# 7. MAIN CHECK
# =========================
def check(vless):
    ip = extract_host(vless)
    if not ip:
        return None

    if not is_in_list(ip):
        return None

    if tcp_test(ip):
        return vless

    return None


# =========================
# 8. RUN
# =========================
nodes = get_sub()
print("TOTAL:", len(nodes))

good = []

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
    for i, res in enumerate(ex.map(check, nodes)):
        print(f"{i+1}/{len(nodes)}")
        if res:
            good.append(res)

print("GOOD NODES:", len(good))

with open("good.txt", "w") as f:
    f.write("\n".join(good))

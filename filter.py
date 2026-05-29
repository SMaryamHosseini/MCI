import requests
import base64
import re
from urllib.parse import urlparse, parse_qs

SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

good = set()

# ---------- decode ----------
def decode_sub(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return text

# ---------- valid domain ----------
def valid_domain(host):

    host = host.strip().lower()

    if len(host) > 60:
        return False

    if "#" in host:
        return False

    if " " in host:
        return False

    if not re.match(r'^[a-z0-9\.\-]+$', host):
        return False

    if "." not in host:
        return False

    # حذف ip
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', host):
        return False

    # blacklist
    bad = [
        "cloudflare",
        "akamai",
        "cdn",
        "workers",
        "speedtest",
        "google.com",
        "play.google.com"
    ]

    for b in bad:
        if b in host:
            return False

    return True

# ---------- process ----------
for sub in SUBS:

    print("FETCH:", sub)

    try:
        raw = requests.get(sub, timeout=20).text
        decoded = decode_sub(raw)

    except Exception as e:
        print("SUB ERROR:", e)
        continue

    lines = decoded.splitlines()

    print("LINES:", len(lines))

    for line in lines:

        line = line.strip()

        if not line.startswith("vless://"):
            continue

        lower = line.lower()

        # فقط ws
        if "type=ws" not in lower:
            continue

        # فقط no tls
        if "security=tls" in lower:
            continue

        if "security=reality" in lower:
            continue

        # فقط 80/8080
        m = re.search(r'@[^:]+:(\d+)', line)

        if not m:
            continue

        port = m.group(1)

        if port not in ["80", "8080"]:
            continue

        try:

            parsed = urlparse(line)

            query = parse_qs(parsed.query)

            host = None

            if "host" in query:
                host = query["host"][0]

            elif "sni" in query:
                host = query["sni"][0]

            if not host:
                continue

            if valid_domain(host):
                good.add(line)

        except:
            pass

# ---------- save ----------
good = sorted(list(good))

with open("mci.txt", "w", encoding="utf-8") as f:

    for x in good:
        f.write(x + "\n")

print("DONE")
print("GOOD:", len(good))

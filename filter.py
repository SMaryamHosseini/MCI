import requests
import base64
import re

SUB_LINKS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

CDN_PREFIXES = [
    "23.", "2.", "184.", "104.", "172.", "96.", "69.", "95."
]

good = []

def extract_ip(line):
    m = re.search(r'@([\d\.]+):', line)
    return m.group(1) if m else None

for sub in SUB_LINKS:
    print("FETCH:", sub)

    try:
        raw = requests.get(sub, timeout=20).text

        # base64 decode
        try:
            decoded = base64.b64decode(raw).decode("utf-8", errors="ignore")
        except:
            decoded = raw

        lines = decoded.splitlines()
        print("LINES:", len(lines))

        for line in lines:
            if "vless://" not in line:
                continue

            ip = extract_ip(line)
            if not ip:
                continue

            for p in CDN_PREFIXES:
                if ip.startswith(p):
                    good.append(line)
                    break

    except Exception as e:
        print("ERROR:", e)

good = list(set(good))

print("FOUND:", len(good))

with open("mci_best.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(good))

with open("sub.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(good))

print("DONE")

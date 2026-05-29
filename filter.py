import requests
import re
import socket
import base64
import time

SUB_LINKS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

PORT = 443
TIMEOUT = 2

# ISP hints (NOT strict, only labeling)
ISP_HINTS = {
    "mci": ["mcinet", "mci", "telecommunication"],
    "irancell": ["irancell", "mtni", "mtn"],
}

def decode_base64_if_needed(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return text

def extract_ips(text):
    # IPv4 regex
    return re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', text)

def tcp_check(ip, port=443):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        start = time.time()
        result = s.connect_ex((ip, port))
        latency = int((time.time() - start) * 1000)
        s.close()

        if result == 0:
            return True, latency
        return False, -1
    except:
        return False, -1

def guess_isp(ip):
    # weak heuristic only (optional)
    for isp, keywords in ISP_HINTS.items():
        if any(k in ip.lower() for k in keywords):
            return isp
    return "unknown"

good_mci = []
good_irancell = []
dead = []

for sub in SUB_LINKS:
    print("FETCH:", sub)

    try:
        text = requests.get(sub, timeout=20).text
        text = decode_base64_if_needed(text)

        ips = extract_ips(text)
        ips = list(set(ips))

        print("TOTAL IPS:", len(ips))

        for i, ip in enumerate(ips):
            ok, ping = tcp_check(ip)

            isp = guess_isp(ip)

            print(f"{i+1}/{len(ips)} {ip} -> {ping}ms")

            if ok:
                if isp == "mci":
                    good_mci.append(ip)
                elif isp == "irancell":
                    good_irancell.append(ip)
                else:
                    # unknown but alive
                    good_irancell.append(ip)
            else:
                dead.append(ip)

    except Exception as e:
        print("ERROR:", e)

good_mci = list(set(good_mci))
good_irancell = list(set(good_irancell))

with open("mci_best.txt", "w") as f:
    for x in good_mci:
        f.write(x + "\n")

with open("irancell_best.txt", "w") as f:
    for x in good_irancell:
        f.write(x + "\n")

print("\nRESULTS")
print("MCI:", len(good_mci))
print("IRANCELL:", len(good_irancell))
print("DEAD:", len(dead))
print("DONE")

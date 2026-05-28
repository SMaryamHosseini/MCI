import requests
import socket
import base64

allowed = open("allowed_ranges.txt").read().splitlines()
subs = open("subs.txt").read().splitlines()

good = []

for sub in subs:

    try:
        r = requests.get(sub, timeout=20)

        data = r.text.strip()

        try:
            decoded = base64.b64decode(data + "===").decode(errors="ignore")
        except:
            continue

        for line in decoded.splitlines():

            if not line.startswith("vless://"):
                continue

            try:
                host = line.split("@")[1].split(":")[0]

                ip = socket.gethostbyname(host)

                if any(ip.startswith(x) for x in allowed):
                    good.append(line)

            except:
                pass

    except:
        pass

output = "\n".join(good)

encoded = base64.b64encode(output.encode()).decode()

open("mci.txt","w").write(encoded)

print("saved", len(good))

import json
import csv
import time

def export_to_json(cookies, filename=None):
    if not filename:
        filename = f"cookies_{int(time.time())}.json"
    with open(filename, "w") as f:
        json.dump(cookies, f, indent=4)
    print(f"[+] Cookies diexport ke {filename}")

def export_to_csv(cookies, filename=None):
    if not filename:
        filename = f"cookies_{int(time.time())}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Value"])
        for k, v in cookies.items():
            writer.writerow([k, v])
    print(f"[+] Cookies diexport ke {filename}")

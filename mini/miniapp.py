import time
import json
import hashlib
import requests
from fastapi import FastAPI
from threading import Thread
import uvicorn
import random

app = FastAPI()

LAST_DATA = {}
COMPUTED_RESULT = {}

def compute_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def fetch_iss_position():
    response = requests.get("http://api.open-notify.org/iss-now.json")
    return response.json()

def fetch_ip():
    response = requests.get("https://api.ipify.org?format=json")
    return response.json()

def detect_changes(old, new):
    if not old:
        return True
    return compute_hash(old) != compute_hash(new)

def simple_compute(data1, data2):
    return random.random()

def polling_loop():
    print("Polling thread started")
    global LAST_DATA, COMPUTED_RESULT
    while True:
        try:
            iss_data = fetch_iss_position()
            ip_data = fetch_ip()

            changed = False

            if detect_changes(LAST_DATA.get("iss"), iss_data):
                LAST_DATA["iss"] = iss_data
                changed = True

            if detect_changes(LAST_DATA.get("ip"), ip_data):
                LAST_DATA["ip"] = ip_data
                changed = True

            if changed:
                COMPUTED_RESULT = simple_compute(LAST_DATA.get("iss", {}), LAST_DATA.get("ip", {}))
                print("Data changed, updated computed result:", COMPUTED_RESULT)
            else:
                print("No change detected")

        except Exception as e:
            print(f"Polling error: {e}")

        time.sleep(10)

@app.get("/latest")
def get_latest():
    return {
        "iss": LAST_DATA.get("iss"),
        "ip": LAST_DATA.get("ip"),
        "computed": COMPUTED_RESULT
    }

if __name__ == "__main__":
    Thread(target=polling_loop, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)

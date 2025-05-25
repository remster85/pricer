import time
import json
import hashlib
import requests
from fastapi import FastAPI
from threading import Thread, Lock
import uvicorn
import random

app = FastAPI()

# State
LAST_DATA = {}
COMPUTED_RESULT = None
_changed_since_last_compute = False
_lock = Lock()

# Configuration
FETCH_INTERVALS = {
    "iss": 5,
    "ip": 15,
}
COMPUTE_INTERVAL = 5  # seconds

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

def fetch_loop(key, fetch_fn, interval):
    global _changed_since_last_compute
    while True:
        try:
            data = fetch_fn()
            with _lock:
                if detect_changes(LAST_DATA.get(key), data):
                    LAST_DATA[key] = data
                    _changed_since_last_compute = True
                    print(f"[{key}] Data changed.")
                else:
                    print(f"[{key}] No change.")
        except Exception as e:
            print(f"[{key}] Fetch error: {e}")
        time.sleep(interval)

def compute_loop():
    global COMPUTED_RESULT, _changed_since_last_compute
    while True:
        time.sleep(COMPUTE_INTERVAL)
        with _lock:
            if _changed_since_last_compute:
                COMPUTED_RESULT = simple_compute(
                    LAST_DATA.get("iss", {}),
                    LAST_DATA.get("ip", {})
                )
                print("[COMPUTE] Updated result:", COMPUTED_RESULT)
                _changed_since_last_compute = False
            else:
                print("[COMPUTE] No changes to compute.")

@app.get("/latest")
def get_latest():
    with _lock:
        return {
            "iss": LAST_DATA.get("iss"),
            "ip": LAST_DATA.get("ip"),
            "computed": COMPUTED_RESULT
        }

def start_polling_threads():
    Thread(target=fetch_loop, args=("iss", fetch_iss_position, FETCH_INTERVALS["iss"]), daemon=True).start()
    Thread(target=fetch_loop, args=("ip", fetch_ip, FETCH_INTERVALS["ip"]), daemon=True).start()
    Thread(target=compute_loop, daemon=True).start()

if __name__ == "__main__":
    start_polling_threads()
    uvicorn.run(app, host="127.0.0.1", port=8000)

import time
import json
import hashlib
import os
from datetime import datetime
import requests

CHANGE_DIR = "changes"
os.makedirs(CHANGE_DIR, exist_ok=True)

POLL_INTERVAL = 10  # seconds
SAVE_DIR = "history"
LAST_DIR = "last"

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(LAST_DIR, exist_ok=True)

def compute_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def load_last_data(name):
    path = os.path.join(LAST_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def update_last_data(name, data):
    path = os.path.join(LAST_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def save_versioned_data(name, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SAVE_DIR, f"{name}_{timestamp}.json")
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ [{name}] New version saved: {filename}")

def detect_changes(old, new, prefix=""):
    changes = []
    if isinstance(old, dict) and isinstance(new, dict):
        keys = set(old.keys()) | set(new.keys())
        for key in keys:
            old_val = old.get(key)
            new_val = new.get(key)
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(old_val, dict) and isinstance(new_val, dict):
                changes.extend(detect_changes(old_val, new_val, prefix=full_key))
            elif old_val != new_val:
                changes.append((full_key, old_val, new_val))
    elif old != new:
        changes.append((prefix, old, new))
    return changes

def monitor(name, fetch_func):
    last_data = load_last_data(name)
    last_hash = compute_hash(last_data) if last_data else None

    try:
        current_data = fetch_func()
        if current_data is None:
            print(f"⚠️  [{name}] No data fetched.")
            return

        current_hash = compute_hash(current_data)
        if current_hash != last_hash:
            save_versioned_data(name, current_data)
            update_last_data(name, current_data)

            if last_data:
                changes = detect_changes(last_data, current_data)
                print(f"🔍 [{name}] Changes detected:")
                for field, old_value, new_value in changes:
                    print(f"  • {field}: {old_value} → {new_value}")

                # 💾 Save changes to disk
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                change_path = os.path.join(CHANGE_DIR, f"{name}_changes_{timestamp}.json")
                with open(change_path, "w") as f:
                    json.dump(
                        [{"field": field, "old": old_value, "new": new_value} for field, old_value, new_value in changes],
                        f,
                        indent=2
                    )
                print(f"📁 [{name}] Changes written to: {change_path}")
            else:
                print(f"🆕 [{name}] First snapshot saved.")
        else:
            print(f"✅ [{name}] No changes.")
    except Exception as e:
        print(f"❌ [{name}] Error: {e}")


# Example fetch functions
def fetch_iss_position():
    response = requests.get("http://api.open-notify.org/iss-now.json")
    return response.json()

def fetch_ip():
    response = requests.get("https://api.ipify.org?format=json")
    return response.json()

MONITOR_TASKS = {
    "iss_position": fetch_iss_position,
    "public_ip": fetch_ip,
}

def main():
    while True:
        for name, func in MONITOR_TASKS.items():
            monitor(name, func)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()

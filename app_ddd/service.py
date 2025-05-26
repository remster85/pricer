import time
import random
from threading import Thread

def simple_compute(data1: dict, data2: dict):
    return random.random()

def compute_loop(engine, interval=5):
    def _loop():
        while True:
            time.sleep(interval)
            if engine.has_changed():
                data = engine.get_data()
                result = simple_compute(
                    data.get("iss").to_dict() if data.get("iss") else {},
                    data.get("ip").to_dict() if data.get("ip") else {}
                )
                engine.set_computed_result(result)
                engine.clear_changed()
                print("[COMPUTE] Updated result:", result)
            else:
                print("[COMPUTE] No changes to compute.")
    Thread(target=_loop, daemon=True).start()
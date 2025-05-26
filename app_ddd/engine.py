import time
from threading import Thread, Lock
from typing import Dict
from app.types import ComparableData, Fetchable

class Engine:
    def __init__(self):
        self._data: Dict[str, ComparableData] = {}
        self._handlers: Dict[str, Fetchable] = {}
        self._intervals: Dict[str, int] = {}
        self._lock = Lock()
        self._changed = False
        self._computed_result = None

    def register(self, key: str, handler: Fetchable, refresh_interval: int):
        self._handlers[key] = handler
        self._intervals[key] = refresh_interval
        Thread(target=self._fetch_loop, args=(key,), daemon=True).start()

    def _fetch_loop(self, key: str):
        interval = self._intervals[key]
        handler = self._handlers[key]

        while True:
            try:
                new_data = handler.fetch()
                with self._lock:
                    old_data = self._data.get(key)
                    if new_data.compare(old_data):
                        self._data[key] = new_data
                        self._changed = True
                        print(f"[{key}] Data changed.")
                    else:
                        print(f"[{key}] No change.")
            except Exception as e:
                print(f"[{key}] Fetch error: {e}")
            time.sleep(interval)

    def get_data(self) -> Dict[str, ComparableData]:
        with self._lock:
            return dict(self._data)

    def get_latest(self) -> dict:
        with self._lock:
            return {
                k: v.to_dict() for k, v in self._data.items()
            } | {
                "computed": self._computed_result
            }

    def has_changed(self) -> bool:
        with self._lock:
            return self._changed

    def clear_changed(self):
        with self._lock:
            self._changed = False

    def set_computed_result(self, result):
        with self._lock:
            self._computed_result = result
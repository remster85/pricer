from app.types import ComparableData
import hashlib
import json

class IPData(ComparableData):
    def __init__(self, raw_data: dict):
        self.raw = raw_data
        self._hash = self._compute_hash()

    def _compute_hash(self):
        return hashlib.sha256(json.dumps(self.raw, sort_keys=True).encode()).hexdigest()

    def compare(self, other: ComparableData | None) -> bool:
        if other is None or not isinstance(other, IPData):
            return True
        return self._hash != other._hash

    def to_dict(self):
        return self.raw
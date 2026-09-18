from hashlib import sha256
from math import log
from threading import RLock
from flask import Flask, jsonify, request

app = Flask(__name__)


class HyperLogLog:
    def __init__(self, precision=10):
        if not 4 <= precision <= 16:
            raise ValueError("precision must be between 4 and 16")
        self.precision = precision
        self.register_count = 1 << precision
        self.registers = [0] * self.register_count
        self.lock = RLock()

    def _hash(self, value):
        return int.from_bytes(sha256(value.encode()).digest()[:8], "big")

    def add(self, value):
        if not isinstance(value, str) or not value:
            raise ValueError("value must be a non-empty string")
        hashed = self._hash(value)
        index = hashed >> (64 - self.precision)
        remaining = 64 - self.precision
        remainder = hashed & ((1 << remaining) - 1)
        rank = remaining + 1 if remainder == 0 else remaining - remainder.bit_length() + 1
        with self.lock:
            self.registers[index] = max(self.registers[index], rank)

    def count(self):
        with self.lock:
            m = self.register_count
            indicator = sum(2.0 ** (-v) for v in self.registers)
            alpha = 0.673 if m == 16 else 0.697 if m == 32 else 0.709 if m == 64 else 0.7213 / (1 + 1.079 / m)
            estimate = alpha * m * m / indicator
            zeros = self.registers.count(0)
            if estimate <= 2.5 * m and zeros:
                estimate = m * log(m / zeros)
            return int(round(estimate))

    def stats(self):
        with self.lock:
            return {"precision": self.precision, "registers": self.register_count,
                    "non_zero_registers": sum(v > 0 for v in self.registers),
                    "estimated_unique": self.count()}


hll = HyperLogLog()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "hyperloglog"})


@app.post("/api/items")
def add_item():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get("value"), str) or not body["value"]:
        return jsonify({"error": "non-empty string 'value' is required"}), 400
    hll.add(body["value"])
    return jsonify({"added": True, "estimated_unique": hll.count()}), 201


@app.post("/api/items/batch")
def add_batch():
    body = request.get_json(silent=True)
    values = body.get("values") if isinstance(body, dict) else None
    if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
        return jsonify({"error": "non-empty string list 'values' is required"}), 400
    for value in values:
        hll.add(value)
    return jsonify({"added": len(values), "estimated_unique": hll.count()}), 201


@app.get("/api/count")
def count():
    return jsonify({"estimated_unique": hll.count()})


@app.get("/api/stats")
def stats():
    return jsonify(hll.stats())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

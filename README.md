# HyperLogLog

A Flask service demonstrating HyperLogLog, a probabilistic data structure for estimating the number of unique items in a large stream.

## Features

- Approximate unique-count estimation
- Configurable precision
- SHA-256 hashing
- Duplicate-resistant cardinality estimation
- Batch ingestion
- Thread-safe operations
- Register statistics
- Health endpoint
- Pytest test suite

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/items` | Add one item |
| POST | `/api/items/batch` | Add many items |
| GET | `/api/count` | Get estimated unique count |
| GET | `/api/stats` | HLL statistics |

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows:

```powershell
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Run tests:

```bash
pytest -q
```

## Example

```bash
curl -X POST http://localhost:5000/api/items -H "Content-Type: application/json" -d '{"value":"user-100"}'
curl http://localhost:5000/api/count
```

## Architecture

```text
Unique Item
    |
    v
SHA-256 Hash
    |
    v
HLL Registers
    |
    v
Cardinality Estimator
    |
    v
Estimated Unique Count
```

## Learning Goals

Cardinality estimation, probabilistic data structures, hashing, streaming analytics, memory-efficient counting, and techniques used in analytics platforms, databases, telemetry systems, and distributed applications.

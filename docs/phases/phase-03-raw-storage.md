# Phase 03 — Raw Storage: MinIO Object Store & Parquet Lake

## Objective
Implement raw object storage for HTML/JSON payloads in MinIO and compressed Parquet files for long-term analytical storage.

## Alignment with problem statement & feasibility
Provides data lineage auditability and high-performance analytical storage.

## Prerequisites
Phase 02 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| MinIO Client | 7.2.7 | S3 compatible storage |
| PyArrow | 16.1.0 | Parquet conversion |

## Repo layout after this phase
```
prometheus/storage/
├── __init__.py
├── minio_client.py
└── parquet_writer.py
```

## Implementation Steps
### Step 1: MinIO Client in `prometheus/storage/minio_client.py`
```python
from minio import Minio
from prometheus.config import settings
import io

class StorageManager:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )

    def save_raw(self, bucket: str, object_name: str, content: bytes):
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)
        self.client.put_object(bucket, object_name, io.BytesIO(content), len(content))
```

## Deliverables
- `prometheus/storage/minio_client.py`
- `prometheus/storage/parquet_writer.py`
- `tests/unit/test_storage.py`

## Definition of Done
```bash
pytest tests/unit/test_storage.py
```

## Out of Scope
AWS S3 multi-region replication.

## Notes
Partition parquet files by year/month/day/route.

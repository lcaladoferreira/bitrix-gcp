import json
import gzip
from datetime import datetime
from typing import List, Dict, Any
from google.cloud import storage
from bitrix_gcp.errors import StorageError
from bitrix_gcp.schemas import calculate_payload_hash

class StorageClient:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_jsonl(self, records: List[Dict[str, Any]], entity_name: str,
                    batch_id: str, part_number: int,
                    compress: bool = False) -> str:
        load_date = datetime.now().strftime("%Y-%m-%d")
        file_ext = "jsonl.gz" if compress else "jsonl"
        blob_name = f"bitrix/{entity_name}/load_date={load_date}/batch_id={batch_id}/part-{part_number:05d}.{file_ext}"
        blob = self.bucket.blob(blob_name)
        extracted_at = datetime.now().isoformat()

        processed = []
        for rec in records:
            item = {
                "ID": rec.get("ID"),
                "TITLE": rec.get("TITLE"),
                "DATE_CREATE": rec.get("DATE_CREATE"),
                "DATE_MODIFY": rec.get("DATE_MODIFY"),
                "STAGE_ID": rec.get("STAGE_ID"),
                "OPPORTUNITY": rec.get("OPPORTUNITY"),
                "NAME": rec.get("NAME"),
                "LAST_NAME": rec.get("LAST_NAME"),
                "STATUS_ID": rec.get("STATUS_ID"),
                "SUBJECT": rec.get("SUBJECT"),
                "CREATED": rec.get("CREATED"),
                "LAST_UPDATED": rec.get("LAST_UPDATED"),
                "payload": rec,
                "metadata": {
                    "batch_id": batch_id,
                    "extracted_at": extracted_at,
                    "source_entity": entity_name,
                    "source_system": "bitrix24",
                    "raw_payload_hash": calculate_payload_hash(rec)
                }
            }
            processed.append(json.dumps(item, ensure_ascii=False))

        content = "\n".join(processed).encode("utf-8")
        if compress:
            content = gzip.compress(content)

        try:
            blob.upload_from_string(content, content_type="application/x-ndjson", timeout=60)
            return f"gs://{self.bucket_name}/{blob_name}"
        except Exception as e:
            raise StorageError(f"GCS Upload failed: {str(e)}")

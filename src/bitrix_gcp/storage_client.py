import json
import gzip
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.cloud import storage
from src.bitrix_gcp.logging_config import logger
from src.bitrix_gcp.errors import StorageError

class StorageClient:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_jsonl(self, records: List[Dict[str, Any]], entity_name: str,
                    batch_id: str, part_number: int,
                    compress: bool = False) -> str:
        """
        Uploads records as JSONL to GCS with deterministic paths.
        gs://bucket/bitrix/entity_name/load_date=YYYY-MM-DD/batch_id=.../part-00001.jsonl
        """
        load_date = datetime.utcnow().strftime("%Y-%m-%d")
        file_ext = "jsonl.gz" if compress else "jsonl"
        blob_name = f"bitrix/{entity_name}/load_date={load_date}/batch_id={batch_id}/part-{part_number:05d}.{file_ext}"

        blob = self.bucket.blob(blob_name)

        # Prepare content with metadata
        extracted_at = datetime.utcnow().isoformat()
        processed_data = []
        for rec in records:
            # We wrap the record to match the required BQ schema:
            # Structured columns + 'payload' (full record) + 'metadata'
            rec_with_meta = {
                "ID": rec.get("ID"),
                "TITLE": rec.get("TITLE"),
                "DATE_CREATE": rec.get("DATE_CREATE"),
                "DATE_MODIFY": rec.get("DATE_MODIFY"),
                "STAGE_ID": rec.get("STAGE_ID"),
                "OPPORTUNITY": rec.get("OPPORTUNITY"),
                "CURRENCY_ID": rec.get("CURRENCY_ID"),
                "ASSIGNED_BY_ID": rec.get("ASSIGNED_BY_ID"),
                "payload": rec,  # The full original record
                "metadata": {
                    "batch_id": batch_id,
                    "extracted_at": extracted_at,
                    "source_entity": entity_name,
                    "source_system": "bitrix24"
                }
            }
            processed_data.append(json.dumps(rec_with_meta, ensure_ascii=False))

        content = "\n".join(processed_data).encode("utf-8")

        if compress:
            content = gzip.compress(content)

        try:
            blob.upload_from_string(content, content_type="application/x-ndjson")
            uri = f"gs://{self.bucket_name}/{blob_name}"
            logger.info(f"Uploaded chunk to {uri}", extra={"records": len(records)})
            return uri
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {str(e)}")
            raise StorageError(f"GCS Upload failed: {str(e)}")

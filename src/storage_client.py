import os
import json
import uuid
from datetime import datetime
from google.cloud import storage
from src.logger import logger

class StorageClient:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_jsonl_chunk(self, records: list, entity: str) -> str:
        """
        Uploads a list of records as a JSONL file to GCS.
        Path structure: gs://<bucket>/bitrix/<entity>/YYYY/MM/DD/<entity>_<timestamp>_<uuid>.jsonl
        """
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        timestamp = now.strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex

        blob_name = f"bitrix/{entity}/{date_path}/{entity}_{timestamp}_{unique_id}.jsonl"
        blob = self.bucket.blob(blob_name)

        processed_records = []
        for record in records:
            processed_record = {
                "ID": record.get("ID"),
                "TITLE": record.get("TITLE"),
                "DATE_CREATE": record.get("DATE_CREATE"),
                "DATE_MODIFY": record.get("DATE_MODIFY"),
                "STAGE_ID": record.get("STAGE_ID"),
                "OPPORTUNITY": record.get("OPPORTUNITY"),
                "payload": record # The full record as a dict, will be serialized to JSON
            }
            processed_records.append(processed_record)

        jsonl_content = "\n".join([json.dumps(rec, ensure_ascii=False) for rec in processed_records])
        blob.upload_from_string(jsonl_content, content_type="application/x-ndjson")

        logger.info(f"Uploaded chunk to {blob_name}", extra={"records_count": len(records), "blob": blob_name})
        return f"gs://{self.bucket_name}/{blob_name}"

    def list_blobs_for_today(self, entity: str):
        now = datetime.utcnow()
        prefix = f"bitrix/{entity}/{now.strftime('%Y/%m/%d')}/"
        return self.client.list_blobs(self.bucket_name, prefix=prefix)

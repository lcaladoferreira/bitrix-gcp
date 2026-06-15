from datetime import datetime
from typing import Optional, Dict, Any
from google.cloud import bigquery
from src.bitrix_gcp.logging_config import logger

class AuditManager:
    def __init__(self, client: bigquery.Client, dataset_id: str):
        self.client = client
        self.table_id = f"{dataset_id}.pipeline_audit"
        self._ensure_audit_table()

    def _ensure_audit_table(self):
        schema = [
            bigquery.SchemaField("batch_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("entity_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("started_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("finished_at", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("records_extracted", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("records_loaded", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("records_merged", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("gcs_paths", "STRING", mode="REPEATED"),
            bigquery.SchemaField("watermark_start", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("watermark_end", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("job_id", "STRING", mode="NULLABLE"),
        ]
        table = bigquery.Table(self.table_id, schema=schema)
        try:
            self.client.get_table(self.table_id)
        except Exception:
            logger.info(f"Creating audit table {self.table_id}")
            self.client.create_table(table)

    def log_start(self, batch_id: str, entity_name: str, watermark_start: Optional[datetime] = None) -> None:
        row = {
            "batch_id": batch_id,
            "entity_name": entity_name,
            "started_at": datetime.utcnow().isoformat(),
            "status": "RUNNING",
            "watermark_start": watermark_start.isoformat() if watermark_start else None,
            "gcs_paths": []
        }
        self.client.insert_rows_json(self.table_id, [row])

    def log_finish(self, batch_id: str, status: str, **kwargs) -> None:
        # Updating rows in BQ is expensive/slow, usually we just insert a new state or use a different strategy.
        # For audit, inserting a new record with the same batch_id is often fine, or using MERGE.
        # Here we'll just insert a completion record.
        row = {
            "batch_id": batch_id,
            "entity_name": kwargs.get("entity_name", "unknown"),
            "started_at": kwargs.get("started_at", datetime.utcnow().isoformat()),
            "finished_at": datetime.utcnow().isoformat(),
            "status": status,
            "records_extracted": kwargs.get("records_extracted"),
            "records_loaded": kwargs.get("records_loaded"),
            "records_merged": kwargs.get("records_merged"),
            "gcs_paths": kwargs.get("gcs_paths", []),
            "watermark_start": kwargs.get("watermark_start"),
            "watermark_end": kwargs.get("watermark_end"),
            "error_message": kwargs.get("error_message"),
            "job_id": kwargs.get("job_id"),
        }
        self.client.insert_rows_json(self.table_id, [row])

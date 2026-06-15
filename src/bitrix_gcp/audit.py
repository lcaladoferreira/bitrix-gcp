from datetime import datetime
from typing import Optional
from google.cloud import bigquery

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
            bigquery.SchemaField("finished_at", "TIMESTAMP"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("records_extracted", "INTEGER"),
            bigquery.SchemaField("records_loaded", "INTEGER"),
            bigquery.SchemaField("records_merged", "INTEGER"),
            bigquery.SchemaField("gcs_paths", "STRING", mode="REPEATED"),
            bigquery.SchemaField("watermark_start", "TIMESTAMP"),
            bigquery.SchemaField("watermark_end", "TIMESTAMP"),
            bigquery.SchemaField("error_message", "STRING"),
        ]
        table = bigquery.Table(self.table_id, schema=schema)
        try:
            self.client.get_table(self.table_id)
        except Exception:
            self.client.create_table(table)

    def log_start(self, batch_id: str, entity_name: str, watermark_start: Optional[str] = None):
        row = {
            "batch_id": batch_id,
            "entity_name": entity_name,
            "started_at": datetime.now().isoformat(),
            "status": "RUNNING",
            "watermark_start": watermark_start
        }
        self.client.insert_rows_json(self.table_id, [row])

    def log_finish(self, batch_id: str, status: str, **kwargs):
        row = {
            "batch_id": batch_id,
            "entity_name": kwargs.get("entity_name"),
            "started_at": datetime.now().isoformat(),
            "finished_at": datetime.now().isoformat(),
            "status": status,
            "records_extracted": kwargs.get("records_extracted"),
            "records_loaded": kwargs.get("records_loaded"),
            "records_merged": kwargs.get("records_merged"),
            "gcs_paths": kwargs.get("gcs_paths", []),
            "error_message": kwargs.get("error_message")
        }
        self.client.insert_rows_json(self.table_id, [row])

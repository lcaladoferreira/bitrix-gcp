from google.cloud import bigquery
from src.logger import logger
from src.config import config

class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client()

    def get_max_date_modify(self, table_id: str) -> str:
        """
        Retrieves the maximum DATE_MODIFY from the target table for incremental sync.
        """
        query = f"SELECT MAX(DATE_MODIFY) as max_date FROM `{table_id}`"
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            for row in results:
                if row.max_date:
                    return row.max_date.isoformat()
        except Exception as e:
            logger.warning(f"Could not retrieve watermark from {table_id} (it might not exist yet): {e}")
        return None

    def load_gcs_to_staging(self, gcs_uris: list, staging_table_id: str):
        """
        Loads JSONL files from GCS into a staging table.
        """
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=False,
            schema=[
                bigquery.SchemaField("ID", "STRING"),
                bigquery.SchemaField("TITLE", "STRING"),
                bigquery.SchemaField("DATE_CREATE", "TIMESTAMP"),
                bigquery.SchemaField("DATE_MODIFY", "TIMESTAMP"),
                bigquery.SchemaField("STAGE_ID", "STRING"),
                bigquery.SchemaField("OPPORTUNITY", "FLOAT"),
                bigquery.SchemaField("payload", "JSON"),
            ],
            ignore_unknown_values=True,
        )

        # We'll also add the payload column to the staging table if we want it there,
        # but since we want the FULL original record, let's rethink.
        # Actually, if we load from JSONL, BigQuery can put the whole JSON into a column if configured.
        # But wait, source_format JSON loads fields into columns.

        # To get the full payload as JSON, we might need to pre-process the records to have a 'payload' field
        # that contains the JSON string of the whole record, or use BQ's JSON type support.

        # In src/storage_client.py, we are dumping the whole record.
        # If we want a 'payload' column, we should probably wrap the record in storage_client.

        load_job = self.client.load_table_from_uri(
            gcs_uris, staging_table_id, job_config=job_config
        )
        load_job.result()
        logger.info(f"Loaded {load_job.output_rows} rows into {staging_table_id}")
        return load_job.output_rows

    def merge_staging_to_final(self, staging_table_id: str, final_table_id: str):
        """
        Performs MERGE/UPSERT from staging to final table.
        Deduplicates staging by ID.
        """
        query = f"""
        MERGE `{final_table_id}` T
        USING (
          SELECT * EXCEPT(rn)
          FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY ID ORDER BY DATE_MODIFY DESC) as rn
            FROM `{staging_table_id}`
          )
          WHERE rn = 1
        ) S
        ON T.ID = S.ID
        WHEN MATCHED THEN
          UPDATE SET
            T.TITLE = S.TITLE,
            T.DATE_MODIFY = S.DATE_MODIFY,
            T.DATE_CREATE = S.DATE_CREATE,
            T.STAGE_ID = S.STAGE_ID,
            T.OPPORTUNITY = S.OPPORTUNITY,
            T.payload = S.payload
        WHEN NOT MATCHED THEN
          INSERT (ID, TITLE, DATE_CREATE, DATE_MODIFY, STAGE_ID, OPPORTUNITY, payload)
          VALUES (ID, TITLE, DATE_CREATE, DATE_MODIFY, STAGE_ID, OPPORTUNITY, payload)
        """
        query_job = self.client.query(query)
        query_job.result()
        logger.info(f"Merged staging table {staging_table_id} into {final_table_id}")

    def ensure_table_exists(self, table_id: str):
        schema = [
            bigquery.SchemaField("ID", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("TITLE", "STRING"),
            bigquery.SchemaField("DATE_CREATE", "TIMESTAMP"),
            bigquery.SchemaField("DATE_MODIFY", "TIMESTAMP"),
            bigquery.SchemaField("STAGE_ID", "STRING"),
            bigquery.SchemaField("OPPORTUNITY", "FLOAT"),
            bigquery.SchemaField("payload", "JSON"),
        ]
        table = bigquery.Table(table_id, schema=schema)
        try:
            self.client.get_table(table_id)
        except Exception:
            logger.info(f"Creating table {table_id}")
            self.client.create_table(table)

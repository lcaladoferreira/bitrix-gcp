from typing import List, Optional
from google.cloud import bigquery
from google.api_core import exceptions
from bitrix_gcp.logging_config import logger
from bitrix_gcp.errors import BigQueryError
from bitrix_gcp.schemas import EntitySchema

class BigQueryClient:
    def __init__(self, project_id: str):
        self.client = bigquery.Client(project=project_id)

    def get_watermark(self, table_id: str, field: str) -> Optional[str]:
        query = f"SELECT MAX({field}) as last_watermark FROM `{table_id}`"
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            for row in results:
                if row.last_watermark:
                    return row.last_watermark.isoformat()
        except exceptions.NotFound:
            logger.warning(f"Table {table_id} not found. Starting from scratch.")
        except Exception as e:
            raise BigQueryError(f"Watermark fetch failed: {str(e)}")
        return None

    def create_table_if_not_exists(self, table_id: str, schema_obj: EntitySchema) -> None:
        def _to_bq_field(f):
            if "fields" in f:
                return bigquery.SchemaField(
                    f["name"], f["type"], mode=f.get("mode", "NULLABLE"),
                    fields=[_to_bq_field(sub) for sub in f["fields"]]
                )
            return bigquery.SchemaField(f["name"], f["type"], mode=f.get("mode", "NULLABLE"))

        bq_schema = [_to_bq_field(f) for f in schema_obj.bq_schema]
        table = bigquery.Table(table_id, schema=bq_schema)
        if schema_obj.partition_field:
            table.time_partitioning = bigquery.TimePartitioning(field=schema_obj.partition_field)
        if schema_obj.clustering_fields:
            table.clustering_fields = schema_obj.clustering_fields

        try:
            self.client.get_table(table_id)
        except exceptions.NotFound:
            logger.info(f"Creating table {table_id}")
            self.client.create_table(table)

    def load_staging(self, uris: List[str], staging_table_id: str, schema_obj: EntitySchema) -> int:
        def _to_bq_field(f):
            if "fields" in f:
                return bigquery.SchemaField(
                    f["name"], f["type"], mode=f.get("mode", "NULLABLE"),
                    fields=[_to_bq_field(sub) for sub in f["fields"]]
                )
            return bigquery.SchemaField(f["name"], f["type"], mode=f.get("mode", "NULLABLE"))

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=[_to_bq_field(f) for f in schema_obj.bq_schema],
            ignore_unknown_values=True,
        )
        load_job = self.client.load_table_from_uri(uris, staging_table_id, job_config=job_config)
        load_job.result()
        return load_job.output_rows

    def merge_to_final(self, staging_table_id: str, final_table_id: str, schema_obj: EntitySchema) -> int:
        fields = [f["name"] for f in schema_obj.bq_schema]
        update_set = ", ".join([f"T.{f} = S.{f}" for f in fields if f != schema_obj.primary_key])
        insert_fields = ", ".join(fields)
        insert_values = ", ".join([f"S.{f}" for f in fields])
        query = f"""
        MERGE `{final_table_id}` T
        USING (
          SELECT * EXCEPT(rn)
          FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY {schema_obj.primary_key} ORDER BY {schema_obj.watermark_field} DESC) as rn
            FROM `{staging_table_id}`
          )
          WHERE rn = 1
        ) S
        ON T.{schema_obj.primary_key} = S.{schema_obj.primary_key}
        WHEN MATCHED THEN
          UPDATE SET {update_set}
        WHEN NOT MATCHED THEN
          INSERT ({insert_fields})
          VALUES ({insert_values})
        """
        query_job = self.client.query(query)
        query_job.result()
        return query_job.num_dml_affected_rows or 0

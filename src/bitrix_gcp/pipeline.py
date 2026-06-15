import uuid
from bitrix_gcp.config import config
from bitrix_gcp.logging_config import logger
from bitrix_gcp.bitrix_client import BitrixClient
from bitrix_gcp.storage_client import StorageClient
from bitrix_gcp.bigquery_client import BigQueryClient
from bitrix_gcp.audit import AuditManager
from bitrix_gcp.schemas import ENTITY_MAP
from bitrix_gcp.errors import PipelineError

class Pipeline:
    def __init__(self):
        self.batch_id = str(uuid.uuid4())
        self.bitrix = BitrixClient(config.BITRIX_WEBHOOK_URL)
        self.storage = StorageClient(config.GCS_BUCKET)
        self.bq = BigQueryClient(config.GCP_PROJECT_ID)
        self.audit = AuditManager(self.bq.client, config.BQ_RAW_DATASET)

    def run(self, entity_name: str):
        schema_obj = ENTITY_MAP.get(entity_name)
        if not schema_obj:
            raise PipelineError(f"Entity {entity_name} not supported.")

        logger.info(f"Starting {entity_name} pipeline", extra={"batch_id": self.batch_id})

        final_table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_FINAL_DATASET}.{entity_name}"
        staging_table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_STAGING_DATASET}.{entity_name}_staging"

        watermark_start = None
        if config.FORCE_FULL_SYNC:
            logger.info("FORCE_FULL_SYNC is TRUE")
        elif config.START_DATE_OVERRIDE:
            watermark_start = config.START_DATE_OVERRIDE
        else:
            watermark_start = self.bq.get_watermark(final_table_id, schema_obj.watermark_field)

        self.audit.log_start(self.batch_id, entity_name, watermark_start=watermark_start)

        gcs_uris = []
        chunk = []
        part = 0
        extracted = 0

        try:
            for record in self.bitrix.get_entities(entity_name, watermark_field=schema_obj.watermark_field, start_date=watermark_start):
                chunk.append(record)
                extracted += 1
                if len(chunk) >= config.CHUNK_SIZE:
                    part += 1
                    gcs_uris.append(self.storage.upload_jsonl(chunk, entity_name, self.batch_id, part))
                    chunk = []

            if chunk:
                part += 1
                gcs_uris.append(self.storage.upload_jsonl(chunk, entity_name, self.batch_id, part))

            if not gcs_uris:
                self.audit.log_finish(self.batch_id, "SUCCESS", entity_name=entity_name, records_extracted=0)
                return

            self.bq.create_table_if_not_exists(staging_table_id, schema_obj)
            loaded = self.bq.load_staging(gcs_uris, staging_table_id, schema_obj)

            self.bq.create_table_if_not_exists(final_table_id, schema_obj)
            merged = self.bq.merge_to_final(staging_table_id, final_table_id, schema_obj)

            self.audit.log_finish(
                self.batch_id, "SUCCESS",
                entity_name=entity_name,
                records_extracted=extracted,
                records_loaded=loaded,
                records_merged=merged,
                gcs_paths=gcs_uris
            )
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            self.audit.log_finish(self.batch_id, "FAILED", entity_name=entity_name, error_message=str(e))
            raise PipelineError(str(e))

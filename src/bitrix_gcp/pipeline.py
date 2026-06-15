import uuid
from datetime import datetime
from typing import List
from src.bitrix_gcp.config import config
from src.bitrix_gcp.logging_config import logger
from src.bitrix_gcp.bitrix_client import BitrixClient
from src.bitrix_gcp.storage_client import StorageClient
from src.bitrix_gcp.bigquery_client import BigQueryClient
from src.bitrix_gcp.audit import AuditManager
from src.bitrix_gcp.schemas import ENTITY_MAP
from src.bitrix_gcp.errors import PipelineError

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

        logger.info(f"Starting pipeline for {entity_name}", extra={"batch_id": self.batch_id})

        final_table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_FINAL_DATASET}.{entity_name}"
        staging_table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_STAGING_DATASET}.{entity_name}_staging"

        # 1. Determine Watermark
        watermark_start = None
        if config.FORCE_FULL_SYNC:
            logger.info("FORCE_FULL_SYNC enabled.")
        elif config.START_DATE_OVERRIDE:
            watermark_start = config.START_DATE_OVERRIDE
            logger.info(f"Using START_DATE_OVERRIDE: {watermark_start}")
        else:
            watermark_start = self.bq.get_watermark(final_table_id, schema_obj.watermark_field)

        self.audit.log_start(self.batch_id, entity_name, watermark_start=None) # Simplifying for now

        # 2. Extract and Stage
        gcs_uris = []
        current_chunk = []
        part_number = 0
        total_extracted = 0

        try:
            for record in self.bitrix.get_entities(entity_name, start_date=watermark_start):
                current_chunk.append(record)
                total_extracted += 1

                if len(current_chunk) >= config.CHUNK_SIZE:
                    part_number += 1
                    uri = self.storage.upload_jsonl(current_chunk, entity_name, self.batch_id, part_number)
                    gcs_uris.append(uri)
                    current_chunk = []

            if current_chunk:
                part_number += 1
                uri = self.storage.upload_jsonl(current_chunk, entity_name, self.batch_id, part_number)
                gcs_uris.append(uri)

            if not gcs_uris:
                logger.info("No records to process.")
                self.audit.log_finish(self.batch_id, "SUCCESS", records_extracted=0, entity_name=entity_name)
                return

            # 3. Load to Staging
            self.bq.create_table_if_not_exists(staging_table_id, schema_obj)
            records_loaded = self.bq.load_staging(gcs_uris, staging_table_id, schema_obj)

            # 4. Merge to Final
            self.bq.create_table_if_not_exists(final_table_id, schema_obj)
            records_merged = self.bq.merge_to_final(staging_table_id, final_table_id, schema_obj)

            self.audit.log_finish(
                self.batch_id,
                "SUCCESS",
                entity_name=entity_name,
                records_extracted=total_extracted,
                records_loaded=records_loaded,
                records_merged=records_merged,
                gcs_paths=gcs_uris
            )
            logger.info(f"Pipeline finished successfully for {entity_name}")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            self.audit.log_finish(self.batch_id, "FAILED", error_message=str(e), entity_name=entity_name)
            raise PipelineError(f"Pipeline failed: {str(e)}")

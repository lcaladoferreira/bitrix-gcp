import os
from src.config import config
from src.logger import logger
from src.bitrix_client import BitrixClient
from src.storage_client import StorageClient
from src.bigquery_client import BigQueryClient

def main():
    logger.info("Starting Bitrix24 to BigQuery sync pipeline")

    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    bitrix = BitrixClient(config.BITRIX_WEBHOOK_URL)
    storage = StorageClient(config.GCS_BUCKET)
    bq = BigQueryClient()

    # Determine start date (watermark)
    start_date = None
    if config.FORCE_FULL_SYNC:
        logger.info("FORCE_FULL_SYNC is enabled. Ignoring watermark.")
    elif config.START_DATE_OVERRIDE:
        start_date = config.START_DATE_OVERRIDE
        logger.info(f"Using START_DATE_OVERRIDE: {start_date}")
    else:
        start_date = bq.get_max_date_modify(config.full_table_id)
        if start_date:
            logger.info(f"Found watermark in BigQuery: {start_date}")
        else:
            start_date = config.DEFAULT_START_DATE
            logger.info(f"No watermark found. Using default start date: {start_date}")

    # Ensure final table exists
    bq.ensure_table_exists(config.full_table_id)

    # Extraction and Staging
    records_chunk = []
    chunk_size = 1000  # Adjust as needed
    gcs_uris = []
    total_records = 0

    for record in bitrix.get_deals(start_date=start_date):
        records_chunk.append(record)
        total_records += 1

        if len(records_chunk) >= chunk_size:
            uri = storage.upload_jsonl_chunk(records_chunk, "deals")
            gcs_uris.append(uri)
            records_chunk = []

    # Upload remaining records
    if records_chunk:
        uri = storage.upload_jsonl_chunk(records_chunk, "deals")
        gcs_uris.append(uri)

    logger.info(f"Extraction complete. Total records extracted: {total_records}. Total files uploaded: {len(gcs_uris)}")

    # Load and Merge
    if gcs_uris:
        bq.load_gcs_to_staging(gcs_uris, config.staging_table_id)
        bq.merge_staging_to_final(config.staging_table_id, config.full_table_id)
        logger.info("Pipeline completed successfully")
    else:
        logger.info("No new records to sync.")

if __name__ == "__main__":
    main()

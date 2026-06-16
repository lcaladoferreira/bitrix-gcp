import argparse
import sys
from bitrix_gcp.config import config
from bitrix_gcp.logging_config import logger
from bitrix_gcp.pipeline import Pipeline
from bitrix_gcp.errors import BitrixGCPError

def main():
    """Entry point for the Bitrix24 to BigQuery pipeline."""
    parser = argparse.ArgumentParser(description="Bitrix24 to BigQuery Data Pipeline")
    parser.add_argument(
        "--entities",
        type=str,
        default=config.ENTITY_NAME,
        help="Comma-separated list of entities to sync (e.g., deals,leads)"
    )
    args = parser.parse_args()

    # Split and clean entity names
    entities = [e.strip() for e in args.entities.split(",") if e.strip()]

    results = []
    any_failed = False

    for entity in entities:
        logger.info(f"Starting sync for entity: {entity}")
        extracted_count = 0
        status = "SUCCESS"

        try:
            pipeline = Pipeline()

            # Senior-level hack: Capture metrics from AuditManager without modifying pipeline.py
            original_log_finish = pipeline.audit.log_finish
            def captured_log_finish(batch_id, status_val, **kwargs):
                nonlocal extracted_count
                extracted_count = kwargs.get("records_extracted", 0)
                return original_log_finish(batch_id, status_val, **kwargs)

            pipeline.audit.log_finish = captured_log_finish

            pipeline.run(entity)
        except BitrixGCPError as e:
            logger.error(f"Pipeline error for {entity}: {str(e)}")
            status = "FAILED"
            any_failed = True
        except Exception as e:
            logger.critical(f"Unexpected system error for {entity}: {str(e)}", exc_info=True)
            status = "ERROR"
            any_failed = True

        results.append({
            "entity": entity,
            "status": status,
            "records": extracted_count
        })

    # Print summary table
    print("\n" + "="*60)
    print(f"{'Entity':<20} | {'Status':<10} | {'Records Extracted':<15}")
    print("-" * 60)
    for res in results:
        print(f"{res['entity']:<20} | {res['status']:<10} | {res['records']:<15}")
    print("="*60 + "\n")

    if any_failed:
        sys.exit(1)

if __name__ == "__main__":
    main()

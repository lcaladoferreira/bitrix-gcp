import sys
from bitrix_gcp.config import config
from bitrix_gcp.logging_config import logger
from bitrix_gcp.pipeline import Pipeline
from bitrix_gcp.errors import BitrixGCPError

def main():
    """Entry point for the Bitrix24 to BigQuery pipeline."""
    try:
        pipeline = Pipeline()
        pipeline.run(config.ENTITY_NAME)
    except BitrixGCPError as e:
        logger.error(f"Pipeline error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected system error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

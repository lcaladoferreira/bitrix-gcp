import sys
from src.bitrix_gcp.config import config
from src.bitrix_gcp.logging_config import logger
from src.bitrix_gcp.pipeline import Pipeline
from src.bitrix_gcp.errors import BitrixGCPError

def main():
    try:
        pipeline = Pipeline()
        pipeline.run(config.ENTITY_NAME)
    except BitrixGCPError as e:
        logger.error(f"Known pipeline error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

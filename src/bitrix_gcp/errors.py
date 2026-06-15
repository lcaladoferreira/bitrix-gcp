class BitrixGCPError(Exception):
    """Base error class."""
    pass

class ConfigurationError(BitrixGCPError):
    """Raised on missing or invalid config."""
    pass

class BitrixAPIError(BitrixGCPError):
    """Raised on API failures."""
    pass

class StorageError(BitrixGCPError):
    """Raised on GCS failures."""
    pass

class BigQueryError(BitrixGCPError):
    """Raised on BigQuery failures."""
    pass

class PipelineError(BitrixGCPError):
    """Raised on orchestration failures."""
    pass

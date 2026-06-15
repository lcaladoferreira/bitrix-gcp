class BitrixGCPError(Exception):
    """Base exception for the pipeline."""
    pass

class ConfigurationError(BitrixGCPError):
    """Raised when environment variables are missing or invalid."""
    pass

class BitrixAPIError(BitrixGCPError):
    """Raised when Bitrix24 API returns an error."""
    pass

class StorageError(BitrixGCPError):
    """Raised when GCS operations fail."""
    pass

class BigQueryError(BitrixGCPError):
    """Raised when BigQuery operations fail."""
    pass

class PipelineError(BitrixGCPError):
    """Raised when the orchestration fails."""
    pass

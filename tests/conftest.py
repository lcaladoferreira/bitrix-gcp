import pytest
from unittest.mock import patch
from collections import namedtuple

MockDeps = namedtuple('MockDeps', ['bitrix', 'storage', 'bq', 'audit'])

@pytest.fixture
def mock_pipeline_deps():
    with patch('bitrix_gcp.pipeline.BitrixClient') as mock_bitrix_cls, \
         patch('bitrix_gcp.pipeline.StorageClient') as mock_storage_cls, \
         patch('bitrix_gcp.pipeline.BigQueryClient') as mock_bq_cls, \
         patch('bitrix_gcp.pipeline.AuditManager') as mock_audit_cls:

        yield MockDeps(
            bitrix=mock_bitrix_cls.return_value,
            storage=mock_storage_cls.return_value,
            bq=mock_bq_cls.return_value,
            audit=mock_audit_cls.return_value
        )

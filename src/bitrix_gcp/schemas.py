import hashlib
import json
from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class EntitySchema:
    name: str
    bq_schema: List[Dict[str, Any]]
    primary_key: str = "ID"
    watermark_field: str = "DATE_MODIFY"
    partition_field: str = "DATE_MODIFY"
    clustering_fields: List[str] = field(default_factory=lambda: ["ID", "STAGE_ID"])

def get_base_schema_fields() -> List[Dict[str, Any]]:
    return [
        {"name": "ID", "type": "STRING", "mode": "REQUIRED"},
        {"name": "payload", "type": "JSON", "mode": "NULLABLE"},
        {"name": "metadata", "type": "RECORD", "mode": "NULLABLE", "fields": [
            {"name": "batch_id", "type": "STRING", "mode": "REQUIRED"},
            {"name": "extracted_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "source_entity", "type": "STRING", "mode": "REQUIRED"},
            {"name": "source_system", "type": "STRING", "mode": "REQUIRED"},
            {"name": "raw_payload_hash", "type": "STRING", "mode": "REQUIRED"},
        ]},
    ]

DEAL_SCHEMA = EntitySchema(
    name="deals",
    bq_schema=get_base_schema_fields() + [
        {"name": "TITLE", "type": "STRING", "mode": "NULLABLE"},
        {"name": "DATE_CREATE", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "DATE_MODIFY", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "STAGE_ID", "type": "STRING", "mode": "NULLABLE"},
        {"name": "OPPORTUNITY", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "CURRENCY_ID", "type": "STRING", "mode": "NULLABLE"},
    ],
    clustering_fields=["ID", "STAGE_ID"]
)

LEAD_SCHEMA = EntitySchema(
    name="leads",
    bq_schema=get_base_schema_fields() + [
        {"name": "TITLE", "type": "STRING", "mode": "NULLABLE"},
        {"name": "NAME", "type": "STRING", "mode": "NULLABLE"},
        {"name": "LAST_NAME", "type": "STRING", "mode": "NULLABLE"},
        {"name": "DATE_CREATE", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "DATE_MODIFY", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "STATUS_ID", "type": "STRING", "mode": "NULLABLE"},
    ],
    clustering_fields=["ID", "STATUS_ID"]
)

CONTACT_SCHEMA = EntitySchema(
    name="contacts",
    bq_schema=get_base_schema_fields() + [
        {"name": "NAME", "type": "STRING", "mode": "NULLABLE"},
        {"name": "LAST_NAME", "type": "STRING", "mode": "NULLABLE"},
        {"name": "DATE_CREATE", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "DATE_MODIFY", "type": "TIMESTAMP", "mode": "NULLABLE"},
    ],
    clustering_fields=["ID"]
)

COMPANY_SCHEMA = EntitySchema(
    name="companies",
    bq_schema=get_base_schema_fields() + [
        {"name": "TITLE", "type": "STRING", "mode": "NULLABLE"},
        {"name": "DATE_CREATE", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "DATE_MODIFY", "type": "TIMESTAMP", "mode": "NULLABLE"},
    ],
    clustering_fields=["ID"]
)

ACTIVITY_SCHEMA = EntitySchema(
    name="activities",
    bq_schema=get_base_schema_fields() + [
        {"name": "SUBJECT", "type": "STRING", "mode": "NULLABLE"},
        {"name": "CREATED", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "LAST_UPDATED", "type": "TIMESTAMP", "mode": "NULLABLE"},
    ],
    primary_key="ID",
    watermark_field="LAST_UPDATED",
    partition_field="LAST_UPDATED",
    clustering_fields=["ID"]
)

ENTITY_MAP = {
    "deals": DEAL_SCHEMA,
    "leads": LEAD_SCHEMA,
    "contacts": CONTACT_SCHEMA,
    "companies": COMPANY_SCHEMA,
    "activities": ACTIVITY_SCHEMA
}

def calculate_payload_hash(payload: Dict[str, Any]) -> str:
    """Calculates a deterministic hash for the payload."""
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

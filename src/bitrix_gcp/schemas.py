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

DEAL_SCHEMA = EntitySchema(
    name="deals",
    bq_schema=[
        {"name": "ID", "type": "STRING", "mode": "REQUIRED"},
        {"name": "TITLE", "type": "STRING", "mode": "NULLABLE"},
        {"name": "DATE_CREATE", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "DATE_MODIFY", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "STAGE_ID", "type": "STRING", "mode": "NULLABLE"},
        {"name": "OPPORTUNITY", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "CURRENCY_ID", "type": "STRING", "mode": "NULLABLE"},
        {"name": "ASSIGNED_BY_ID", "type": "STRING", "mode": "NULLABLE"},
        {"name": "payload", "type": "JSON", "mode": "NULLABLE"},
        {"name": "metadata", "type": "JSON", "mode": "NULLABLE"},
    ],
    primary_key="ID",
    watermark_field="DATE_MODIFY",
    partition_field="DATE_MODIFY",
    clustering_fields=["ID", "STAGE_ID"]
)

# Future schemas for leads, contacts, etc. can be added here
ENTITY_MAP = {
    "deals": DEAL_SCHEMA
}

resource "google_bigquery_dataset" "bitrix_raw" {
  dataset_id = "bitrix_raw"
  location   = var.location
}

resource "google_bigquery_dataset" "bitrix_staging" {
  dataset_id = "bitrix_staging"
  location   = var.location
}

resource "google_bigquery_dataset" "bitrix_final" {
  dataset_id = "bitrix_final"
  location   = var.location
}

resource "google_bigquery_table" "pipeline_audit" {
  dataset_id = google_bigquery_dataset.bitrix_raw.dataset_id
  table_id   = "pipeline_audit"
  deletion_protection = false
  schema = <<EOF
[
  {"name": "batch_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "entity_name", "type": "STRING", "mode": "REQUIRED"},
  {"name": "started_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
  {"name": "finished_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
  {"name": "status", "type": "STRING", "mode": "REQUIRED"},
  {"name": "records_extracted", "type": "INTEGER", "mode": "NULLABLE"},
  {"name": "records_loaded", "type": "INTEGER", "mode": "NULLABLE"},
  {"name": "records_merged", "type": "INTEGER", "mode": "NULLABLE"},
  {"name": "gcs_paths", "type": "STRING", "mode": "REPEATED"},
  {"name": "watermark_start", "type": "TIMESTAMP", "mode": "NULLABLE"},
  {"name": "watermark_end", "type": "TIMESTAMP", "mode": "NULLABLE"},
  {"name": "error_message", "type": "STRING", "mode": "NULLABLE"}
]
EOF
}

resource "google_bigquery_table" "dead_letter" {
  dataset_id = google_bigquery_dataset.bitrix_raw.dataset_id
  table_id   = "dead_letter"
  deletion_protection = false
  schema = <<EOF
[
  {"name": "batch_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "inserted_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
  {"name": "raw_payload", "type": "JSON", "mode": "REQUIRED"},
  {"name": "error_reason", "type": "STRING", "mode": "REQUIRED"}
]
EOF
}

resource "google_bigquery_table" "data_quality_results" {
  dataset_id = google_bigquery_dataset.bitrix_raw.dataset_id
  table_id   = "data_quality_results"
  deletion_protection = false
  schema = <<EOF
[
  {"name": "batch_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "entity_name", "type": "STRING", "mode": "REQUIRED"},
  {"name": "check_name", "type": "STRING", "mode": "REQUIRED"},
  {"name": "check_status", "type": "STRING", "mode": "REQUIRED"},
  {"name": "check_details", "type": "STRING", "mode": "NULLABLE"}
]
EOF
}

variable "location" { type = string }

output "raw_dataset_id" { value = google_bigquery_dataset.bitrix_raw.dataset_id }
output "staging_dataset_id" { value = google_bigquery_dataset.bitrix_staging.dataset_id }
output "final_dataset_id" { value = google_bigquery_dataset.bitrix_final.dataset_id }

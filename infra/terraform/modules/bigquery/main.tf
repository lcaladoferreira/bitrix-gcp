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

variable "location" {}

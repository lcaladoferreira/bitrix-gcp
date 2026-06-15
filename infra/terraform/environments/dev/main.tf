# Main entry point for terraform
module "gcs" {
  source      = "../../modules/gcs"
  bucket_name = "bitrix-sync-staging-dev"
  location    = "us-central1"
}

module "bigquery" {
  source   = "../../modules/bigquery"
  location = "us-central1"
}

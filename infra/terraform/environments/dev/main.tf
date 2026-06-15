module "gcs" {
  source = "../../modules/gcs"
  bucket_name = "dev-bitrix-staging"
  location = "us-central1"
}
module "bigquery" {
  source = "../../modules/bigquery"
  location = "us-central1"
}
module "iam" {
  source = "../../modules/iam"
  project_id = "dev-project"
  service_account_email = "sa@dev-project.iam.gserviceaccount.com"
}
module "secret_manager" {
  source = "../../modules/secret_manager"
  secret_id = "bitrix_webhook"
}
module "cloud_run_job" {
  source = "../../modules/cloud_run_job"
  job_name = "bitrix-sync-dev"
  location = "us-central1"
  image_url = "gcr.io/dev-project/bitrix-sync"
  project_id = "dev-project"
  bucket_name = module.gcs.bucket_name
  service_account_email = "sa@dev-project.iam.gserviceaccount.com"
  secret_name = module.secret_manager.secret_name
}

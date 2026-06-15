provider "google" {
  project = var.project_id
  region  = var.region
}

module "gcs" {
  source      = "../../modules/gcs"
  bucket_name = "${var.project_id}-bitrix-staging-prod"
  location    = var.region
}

module "bigquery" {
  source   = "../../modules/bigquery"
  location = var.region
}

module "iam" {
  source                = "../../modules/iam"
  project_id            = var.project_id
  service_account_email = var.service_account_email
}

module "secret_manager" {
  source    = "../../modules/secret_manager"
  secret_id = "bitrix_webhook_url"
}

module "cloud_run_job" {
  source                = "../../modules/cloud_run_job"
  job_name              = "bitrix-sync-prod"
  location              = var.region
  image_url             = "gcr.io/${var.project_id}/bitrix-sync:latest"
  project_id            = var.project_id
  bucket_name           = module.gcs.bucket_name
  service_account_email = var.service_account_email
  secret_name           = module.secret_manager.secret_name
}

module "cloud_scheduler" {
  source                = "../../modules/cloud_scheduler"
  name                  = "bitrix-sync-prod-trigger"
  schedule              = "0 2 * * *" # Daily at 2am
  region                = var.region
  job_uri               = module.cloud_run_job.job_uri
  service_account_email = var.service_account_email
}

variable "project_id" {}
variable "region" { default = "us-central1" }
variable "service_account_email" {}

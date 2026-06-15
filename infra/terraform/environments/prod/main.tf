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

variable "project_id" { default = "prod-proj" }
variable "region" { default = "us-central1" }
variable "service_account_email" { default = "sa@prod-proj.iam.gserviceaccount.com" }

resource "google_cloud_scheduler_job" "sync_trigger" {
  name     = var.name
  schedule = var.schedule
  region   = var.region
  http_target {
    http_method = "POST"
    uri         = var.job_uri
    oidc_token { service_account_email = var.service_account_email }
  }
}
variable "name" {}
variable "schedule" {}
variable "region" {}
variable "job_uri" {}
variable "service_account_email" {}

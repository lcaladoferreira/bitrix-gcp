resource "google_cloud_scheduler_job" "sync_trigger" {
  name             = var.name
  description      = "Trigger Bitrix Sync"
  schedule         = var.schedule
  region           = var.region
  terminate_after  = "3600s"

  http_target {
    http_method = "POST"
    uri         = var.job_uri

    oidc_token {
      service_account_email = var.service_account_email
    }
  }
}

variable "name" { type = string }
variable "schedule" { type = string }
variable "region" { type = string }
variable "job_uri" { type = string }
variable "service_account_email" { type = string }

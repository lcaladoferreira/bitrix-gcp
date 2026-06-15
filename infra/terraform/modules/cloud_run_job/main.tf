resource "google_cloud_run_v2_job" "bitrix_sync" {
  name     = var.job_name
  location = var.location

  template {
    template {
      service_account = var.service_account_email
      containers {
        image = var.image_url
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "GCS_BUCKET"
          value = var.bucket_name
        }
        env {
          name  = "BITRIX_WEBHOOK_SECRET_NAME"
          value = var.secret_name
        }
      }
    }
  }
}

variable "job_name" {}
variable "location" {}
variable "image_url" {}
variable "project_id" {}
variable "bucket_name" {}
variable "service_account_email" {}
variable "secret_name" {}

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

variable "job_name" { type = string }
variable "location" { type = string }
variable "image_url" { type = string }
variable "project_id" { type = string }
variable "bucket_name" { type = string }
variable "service_account_email" { type = string }
variable "secret_name" { type = string }

output "job_name" {
  value = google_cloud_run_v2_job.bitrix_sync.name
}

output "job_uri" {
  value = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${var.job_name}:run"
}

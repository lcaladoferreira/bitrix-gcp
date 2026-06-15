resource "google_secret_manager_secret" "bitrix_webhook" {
  secret_id = "bitrix_webhook_url"
  replication {
    automatic = true
  }
}

resource "google_project_iam_member" "run_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.service_account_email}"
}

variable "project_id" {}
variable "service_account_email" {}

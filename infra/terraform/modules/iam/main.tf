resource "google_project_iam_member" "sa_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${var.service_account_email}"
}

resource "google_project_iam_member" "sa_bq" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${var.service_account_email}"
}

resource "google_project_iam_member" "sa_bq_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${var.service_account_email}"
}

resource "google_project_iam_member" "sa_secret" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.service_account_email}"
}

variable "project_id" { type = string }
variable "service_account_email" { type = string }

resource "google_artifact_registry_repository" "pipeline_repo" {
  location      = var.location
  repository_id = var.repository_id
  description   = "Docker repository for Bitrix Sync Pipeline"
  format        = "DOCKER"
}

variable "location" { type = string }
variable "repository_id" { type = string }

output "repository_url" {
  value = "${var.location}-docker.pkg.dev/${var.project_id}/${var.repository_id}"
}

variable "project_id" { type = string }

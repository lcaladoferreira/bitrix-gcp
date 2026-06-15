resource "google_storage_bucket" "staging" {
  name          = var.bucket_name
  location      = var.location
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

variable "bucket_name" {
  type        = string
  description = "Name of the GCS bucket for staging"
}

variable "location" {
  type        = string
  description = "GCP region"
}

output "bucket_name" {
  value = google_storage_bucket.staging.name
}

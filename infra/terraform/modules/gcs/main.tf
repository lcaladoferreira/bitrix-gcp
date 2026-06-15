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

variable "bucket_name" {}
variable "location" {}

output "bucket_name" {
  value = google_storage_bucket.staging.name
}

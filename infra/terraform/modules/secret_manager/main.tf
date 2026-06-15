resource "google_secret_manager_secret" "webhook" {
  secret_id = var.secret_id
  replication {
    user_managed {
      replicas {
        location = var.location
      }
    }
  }
}

variable "secret_id" {}
variable "location" {}

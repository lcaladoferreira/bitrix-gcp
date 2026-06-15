resource "google_secret_manager_secret" "webhook" {
  secret_id = var.secret_id
  replication { automatic = true }
}
variable "secret_id" {}
output "secret_name" { value = google_secret_manager_secret.webhook.secret_id }

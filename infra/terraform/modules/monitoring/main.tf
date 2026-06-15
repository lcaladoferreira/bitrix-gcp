resource "google_monitoring_alert_policy" "job_failure" {
  display_name = "Bitrix Sync Job Failure"
  combiner     = "OR"
  conditions {
    display_name = "Cloud Run Job Failed"
    condition_threshold {
      filter     = "resource.type = \"cloud_run_job\" AND metric.type = \"run.googleapis.com/job/completed_execution_count\" AND metric.labels.status = \"failed\""
      duration   = "0s"
      comparison = "COMPARISON_GT"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_COUNT"
      }
      threshold_value = 0
    }
  }
  notification_channels = var.notification_channels
}

variable "notification_channels" {
  type    = list(string)
  default = []
}

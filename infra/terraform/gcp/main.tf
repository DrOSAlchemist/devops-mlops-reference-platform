terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "workflow_artifacts" {
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  labels                      = var.labels
}

variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "GCP region for the artifact bucket."
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "Globally unique bucket name for private workflow artifacts."
  type        = string
}

variable "labels" {
  description = "Ownership and cost-allocation labels."
  type        = map(string)
  default     = { project = "platform-guard", managed_by = "terraform" }
}

output "artifact_bucket" {
  value = google_storage_bucket.workflow_artifacts.name
}
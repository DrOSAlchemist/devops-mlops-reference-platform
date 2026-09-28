terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "workflow_artifacts" {
  bucket = var.bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_public_access_block" "workflow_artifacts" {
  bucket                  = aws_s3_bucket.workflow_artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "workflow_artifacts" {
  bucket = aws_s3_bucket.workflow_artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

variable "region" {
  description = "AWS region for workflow artifacts."
  type        = string
}

variable "bucket_name" {
  description = "Globally unique name for the private artifact bucket."
  type        = string
}

variable "tags" {
  description = "Ownership and cost-allocation tags."
  type        = map(string)
  default     = { project = "platform-guard", managed_by = "terraform" }
}

output "artifact_bucket" {
  value = aws_s3_bucket.workflow_artifacts.bucket
}
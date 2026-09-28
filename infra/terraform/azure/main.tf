terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "workflow_artifacts" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_storage_account" "workflow_artifacts" {
  name                            = var.storage_account_name
  resource_group_name             = azurerm_resource_group.workflow_artifacts.name
  location                        = azurerm_resource_group.workflow_artifacts.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  tags                            = var.tags
}

resource "azurerm_storage_container" "workflow_artifacts" {
  name                  = "workflow-artifacts"
  storage_account_id    = azurerm_storage_account.workflow_artifacts.id
  container_access_type = "private"
}

variable "resource_group_name" {
  description = "Resource group for private workflow artifacts."
  type        = string
}

variable "location" {
  description = "Azure region for the resource group."
  type        = string
}

variable "storage_account_name" {
  description = "Globally unique lowercase Azure Storage account name (3-24 chars)."
  type        = string
}

variable "tags" {
  description = "Ownership and cost-allocation tags."
  type        = map(string)
  default     = { project = "platform-guard", managed_by = "terraform" }
}

output "artifact_container" {
  value = azurerm_storage_container.workflow_artifacts.name
}
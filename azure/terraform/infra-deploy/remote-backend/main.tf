resource "azurerm_resource_group" "remote_backend_rg" {
  name     = var.remote_backend_resource_group_name
  location = var.azure_region

  tags = {
    Name        = var.remote_backend_resource_group_name
    Environment = var.environment
  }
}

resource "azurerm_storage_account" "remote_backend_sa" {
  name                     = lower(join("", [random_string.name.result, "backend"]))
  resource_group_name      = azurerm_resource_group.remote_backend_rg.name
  location                 = azurerm_resource_group.remote_backend_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    Name        = "Terraform Backend Storage"
    Environment = var.environment
  }
}

resource "azurerm_storage_container" "remote_state_container" {
  name                  = var.container_name
  storage_account_id    = azurerm_storage_account.remote_backend_sa.id
  container_access_type = "private"
}

resource "random_string" "name" {
  length  = 8
  special = false
  upper   = false
}

output "backend_storage_account_name" {
  value       = azurerm_storage_account.remote_backend_sa.name
  description = "Name of the Storage Account for remote state"
}

output "backend_container_name" {
  value       = azurerm_storage_container.remote_state_container.name
  description = "Name of the Blob Container for remote state"
}

output "backend_resource_group_name" {
  value       = azurerm_resource_group.remote_backend_rg.name
  description = "Name of the Resource Group for Backend"
}
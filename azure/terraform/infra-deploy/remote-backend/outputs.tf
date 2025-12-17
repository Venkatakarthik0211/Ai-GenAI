output "storage_account_name" {
  value       = azurerm_storage_account.remote_backend_sa.name
  description = "Name of the Azure Storage Account"
}

output "container_name" {
  value       = azurerm_storage_container.remote_state_container.name
  description = "Name of the Azure Blob Container"
}

output "resource_group_name" {
  value       = azurerm_resource_group.remote_backend_rg.name
  description = "Name of the Azure Resource Group"
}
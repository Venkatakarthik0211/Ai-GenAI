
# Backend configuration output
output "storage_account_name" {
  value = module.remote_backend.storage_account_name
}

output "container_name" {
  value = module.remote_backend.container_name
}

output "resource_group_name" {
  value = module.remote_backend.resource_group_name
}
output "vnet_name" {
  value = module.vnet.vnet_name
  description = "Name of the Azure Virtual Network"
}

output "vnet_id" {
  value = module.vnet.vnet_id
  description = "ID of the Azure Virtual Network"
}

output "public_subnet_ids" {
  value = module.vnet.public_subnet_ids
  description = "List of public subnet IDs"
}

output "private_subnet_ids" {
  value = module.vnet.private_subnet_ids
  description = "List of private subnet IDs"
}
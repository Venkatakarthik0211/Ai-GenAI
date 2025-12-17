output "vnet_name" {
  value = azurerm_virtual_network.orchestra_vnet.name
  description = "Name of the Virtual Network"
}

output "vnet_id" {
  value = azurerm_virtual_network.orchestra_vnet.id
  description = "ID of the Virtual Network"
}

output "public_subnet_ids" {
  value = azurerm_subnet.public_subnets[*].id
  description = "List of Public Subnet IDs"
}

output "private_subnet_ids" {
  value = azurerm_subnet.private_subnets[*].id
  description = "List of Private Subnet IDs"
}
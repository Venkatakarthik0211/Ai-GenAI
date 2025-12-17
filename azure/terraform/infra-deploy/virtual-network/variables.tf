variable "prefix" {
  description = "Prefix for the resources"
  type        = string
}

variable "azure_region" {
  description = "Azure region to deploy resources"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
}

variable "nat_gateway_name" {
  description = "Name of the NAT Gateway"
  type        = string
}

variable "nat_gateway_sku" {
  description = "SKU for the NAT Gateway (can be Basic or Standard)"
  type        = string
  default     = "Basic"
}

variable "create_vnet" {
  description = "Boolean to indicate whether to create VNet or use an existing one"
  type        = bool
  default     = true
}
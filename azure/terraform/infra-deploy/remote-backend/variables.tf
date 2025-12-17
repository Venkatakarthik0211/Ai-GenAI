variable "azure_region" {
  description = "Azure region"
  type        = string
}

variable "remote_backend_resource_group_name" {
  description = "Name of the Resource Group for Remote Backend"
  type        = string
}

variable "container_name" {
  description = "Name of the container for Terraform remote state"
  type        = string
  default     = "tfstate"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "dev"
}
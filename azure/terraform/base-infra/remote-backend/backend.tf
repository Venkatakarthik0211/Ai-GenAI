# terraform {
#   backend "azurerm" {
#     key                  = "remote-backend/terraform.tfstate"
#     resource_group_name  = "Personal-Workspace"
#     storage_account_name = "personalworkspacestorage"
#     container_name       = "tfstate"
#   }
# }

# backend.tf (temporary)
terraform {
  # Use local backend temporarily
  backend "local" {
    path = "terraform.tfstate"
  }
}
locals {
  config = yamldecode(file("./dev-config.yaml"))
}

module "remote_backend" {
  source                             = "../../infra-deploy/remote-backend"
  azure_region                       = local.config.azure_region
  remote_backend_resource_group_name = local.config.remote_backend_resource_group_name
  container_name                     = local.config.container_name
  environment                        = local.config.environment
}
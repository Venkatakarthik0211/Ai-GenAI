locals {
  config = var.environment == "dev" ? yamldecode(file("./dev-config.yaml")) : yamldecode(file("./prod-config.yaml"))
}

module "vnet" {
  source                = "../../infra-deploy/virtual-network"
  prefix                = "${local.config.prefix}-${var.environment}"
  azure_region          = local.config.azure_region
  vnet_address_space    = local.config.vnet_address_space
  public_subnet_cidrs   = local.config.public_subnet_cidrs
  private_subnet_cidrs  = local.config.private_subnet_cidrs
  create_vnet           = true
  nat_gateway_name      = "${local.config.nat_gateway_name}-${var.environment}"
  nat_gateway_sku       = local.config.nat_gateway_sku
  resource_group_name   = local.config.resource_group_name
}

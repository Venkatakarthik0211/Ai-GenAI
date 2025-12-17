# Virtual Network
resource "azurerm_virtual_network" "orchestra_vnet" {
  name                = "${var.prefix}-vnet"
  location            = var.azure_region
  resource_group_name = var.resource_group_name
  address_space       = [var.vnet_address_space]

  tags = {
    Name = "${var.prefix}-vnet"
  }
}

# Public Subnets
resource "azurerm_subnet" "public_subnets" {
  count                = length(var.public_subnet_cidrs)
  name                 = "${var.prefix}-public-subnet-${count.index + 1}"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.orchestra_vnet.name
  address_prefixes     = [var.public_subnet_cidrs[count.index]]

}

# Private Subnets
resource "azurerm_subnet" "private_subnets" {
  count                = length(var.private_subnet_cidrs)
  name                 = "${var.prefix}-private-subnet-${count.index + 1}"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.orchestra_vnet.name
  address_prefixes     = [var.private_subnet_cidrs[count.index]]
}

# NAT Gateway
resource "azurerm_nat_gateway" "nat_gateway" {
  name                    = var.nat_gateway_name
  location                = var.azure_region
  resource_group_name     = var.resource_group_name
  sku_name                = var.nat_gateway_sku
  idle_timeout_in_minutes = 10

  tags = {
    Name = "${var.prefix}-natgw"
  }
}

# Public IP for NAT Gateway
resource "azurerm_public_ip" "nat_public_ip" {
  name                = "${var.prefix}-natgw-pip"
  location            = var.azure_region
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    Name = "${var.prefix}-natgw-pip"
  }
}

# Associate Public IP with NAT Gateway
resource "azurerm_nat_gateway_public_ip_association" "natgw_pip_association" {
  nat_gateway_id      = azurerm_nat_gateway.nat_gateway.id
  public_ip_address_id = azurerm_public_ip.nat_public_ip.id
}

# Associate NAT Gateway with Public Subnets
resource "azurerm_subnet_nat_gateway_association" "public_subnets_association" {
  count          = length(azurerm_subnet.public_subnets)
  subnet_id      = azurerm_subnet.public_subnets[count.index].id
  nat_gateway_id = azurerm_nat_gateway.nat_gateway.id
}
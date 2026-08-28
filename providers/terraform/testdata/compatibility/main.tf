terraform {
  required_providers {
    amesh = {
      source = "registry.terraform.io/amesh/amesh"
    }
  }
}
provider "amesh" {
  endpoint = "http://host.docker.internal:8000"
  token    = "development-token"
  tenant   = "default"
}

data "amesh_flow" "schema_probe" {
  key       = "schema-probe"
  namespace = "terraform.compatibility"
}

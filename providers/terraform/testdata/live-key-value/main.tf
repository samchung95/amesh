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

resource "amesh_key_value" "compatibility" {
  key       = "epic-701-provider-smoke"
  namespace = "terraform.compatibility"
  document = jsonencode({
    type  = "STRING"
    value = "terraform-and-opentofu"
  })
}

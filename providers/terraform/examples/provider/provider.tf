terraform {
  required_providers {
    amesh = {
      source  = "amesh/amesh"
      version = "~> 0.1"
    }
  }
}
provider "amesh" {
  endpoint = "http://localhost:8000"
  tenant   = "default"
}

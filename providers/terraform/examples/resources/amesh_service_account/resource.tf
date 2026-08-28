resource "amesh_service_account" "automation" {
  key = "automation"
  document = jsonencode({
    handle       = "automation"
    display_name = "Terraform automation"
    enabled      = true
  })
}

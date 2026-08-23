resource "amesh_binding" "operator" {
  key = "operator-flow-role"
  document = jsonencode({
    principal_id   = "00000000-0000-0000-0000-000000000001"
    principal_type = "USER"
    role_name      = "flow-operator"
    scope_type     = "TENANT"
    tenant_id      = "default"
  })
}

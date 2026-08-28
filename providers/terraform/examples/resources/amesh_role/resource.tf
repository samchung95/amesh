resource "amesh_role" "flow_operator" {
  key = "flow-operator"
  document = jsonencode({
    name         = "flow-operator"
    display_name = "Flow operator"
    permissions  = ["flow:view", "execution:create"]
  })
}

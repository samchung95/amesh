resource "amesh_group" "operators" {
  key = "operators"
  document = jsonencode({
    displayName = "Operators"
    members     = []
  })
}

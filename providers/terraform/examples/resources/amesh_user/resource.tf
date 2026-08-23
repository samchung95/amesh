resource "amesh_user" "operator" {
  key = "operator@example.test"
  document = jsonencode({
    userName    = "operator@example.test"
    displayName = "Example operator"
    active      = true
  })
}

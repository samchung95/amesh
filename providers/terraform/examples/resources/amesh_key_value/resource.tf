resource "amesh_key_value" "environment" {
  key       = "environment"
  namespace = "examples"
  document = jsonencode({
    type  = "STRING"
    value = "development"
  })
}

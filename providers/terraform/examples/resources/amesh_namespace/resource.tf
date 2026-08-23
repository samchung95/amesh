resource "amesh_namespace" "shared" {
  key       = "shared"
  namespace = "examples.shared"
  document  = file("${path.module}/namespace-bundle.json")
}

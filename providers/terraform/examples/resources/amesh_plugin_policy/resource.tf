resource "amesh_plugin_policy" "approved_core" {
  key       = "approved-core"
  namespace = "examples"
  document = jsonencode({
    scope     = "NAMESPACE"
    namespace = "examples"
    effect    = "ALLOW"
    stages    = ["VALIDATION", "EXECUTION"]
    selector  = { package = "amesh.core" }
    reason    = "Approved core package"
  })
}

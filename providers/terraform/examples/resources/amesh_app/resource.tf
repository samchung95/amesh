resource "amesh_app" "launcher" {
  key       = "launcher"
  namespace = "examples"
  document = jsonencode({
    title  = "Example launcher"
    flowId = "hello"
  })
}

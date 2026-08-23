resource "amesh_flow" "hello" {
  key       = "hello"
  namespace = "examples"
  document  = <<-YAML
    id: hello
    namespace: examples
    tasks:
      - id: done
        type: core.return
        value: hello
  YAML
}

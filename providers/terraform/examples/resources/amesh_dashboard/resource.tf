resource "amesh_dashboard" "operations" {
  key = "operations"
  document = jsonencode({
    title      = "Operations"
    visibility = "PRIVATE"
    widgets = [{
      id            = "executions"
      title         = "Executions"
      dataSource    = "EXECUTIONS"
      visualization = "NUMBER"
    }]
  })
}

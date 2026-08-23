resource "amesh_tenant" "team" {
  key = "team"
  document = jsonencode({
    slug        = "team"
    displayName = "Team"
    policy = {
      workerGroups = ["default"]
    }
  })
}

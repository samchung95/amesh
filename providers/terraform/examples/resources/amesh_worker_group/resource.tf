resource "amesh_worker_group" "team_policy" {
  key       = "team-workers"
  namespace = "team"
  document = jsonencode({
    workerGroups = ["default", "team-workers"]
  })
}

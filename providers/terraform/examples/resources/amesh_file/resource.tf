resource "amesh_file" "readme" {
  key       = "README.md"
  namespace = "examples"
  document  = "# Managed by Terraform\n"
}

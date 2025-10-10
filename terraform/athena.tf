# Athena Workgroup

resource "aws_athena_workgroup" "project2" {
  name = "project2-athena-wg"

  configuration {
    result_configuration {
      output_location = "s3://${var.s3_bucket_name}/silver/athena/"
    }

    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true
  }

  description = "Athena workgroup for querying Glue Data Catalog (silver and gold lyers)"
}

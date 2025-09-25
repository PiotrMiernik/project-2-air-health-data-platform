# Athena Workgroup
resource "aws_athena_workgroup" "project2" {
  name = "project2-athena-wg"

  configuration {
    result_configuration {
      output_location = "s3://${var.s3_bucket_name}/athena-results/"
    }

    enforce_workgroup_configuration = true
    publish_cloudwatch_metrics_enabled = true
  }

  description = "Athena workgroup for querying Glue Data Catalog (bronze, silver, gold)"
}

# Athena Databases (Glue-backed)

# Bronze layer
resource "aws_athena_database" "bronze" {
  name   = "air_health_bronze"
  bucket = var.s3_bucket_name

  comment = "Athena access to Glue Data Catalog - Bronze layer (raw data)"
}

# Silver layer
resource "aws_athena_database" "silver" {
  name   = "air_health_silver"
  bucket = var.s3_bucket_name

  comment = "Athena access to Glue Data Catalog - Silver layer (transformed data)"
}

# Gold layer
resource "aws_athena_database" "gold" {
  name   = "air_health_gold"
  bucket = var.s3_bucket_name

  comment = "Athena access to Glue Data Catalog - Gold layer (business-ready data)"
}

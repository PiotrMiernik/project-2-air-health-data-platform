# AWS Glue Databases

# Bronze layer (raw data - no crawlers here)
resource "aws_glue_catalog_database" "bronze_db" {
  name        = "air_health_bronze"
  description = "Glue database for raw (bronze) air quality and health data"
}

# Silver layer (cleaned/transformed)
resource "aws_glue_catalog_database" "silver_db" {
  name        = "air_health_silver"
  description = "Glue database for cleaned/transformed (silver) data"
}

# Gold layer (business-ready)
resource "aws_glue_catalog_database" "gold_db" {
  name        = "air_health_gold"
  description = "Glue database for business-ready (gold) data"
}

# AWS Glue Crawler (only for Silver)

resource "aws_glue_crawler" "silver" {
  name          = "project2-silver-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.silver_db.name

  s3_target {
    path = "s3://${var.s3_bucket_name}/silver/"
  }

  schedule = "cron(0 6 * * ? *)" # daily at 6 AM UTC (optional)
}

# AWS Glue Job (Bronze -> Silver ETL)

resource "aws_glue_job" "bronze_to_silver" {
  name     = "bronze-to-silver-job"
  role_arn = aws_iam_role.glue_service_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.s3_bucket_name}/scripts/bronze_to_silver.py"
    python_version  = "3"
  }

  glue_version      = "4.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  default_arguments = {
    "--TempDir"        = "s3://${var.s3_bucket_name}/tmp/"
    "--enable-metrics" = "true"
    "--job-language"   = "python"
  }
}

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

# AWS Glue Job (Bronze -> Silver ETL)

# ECDC Glue Job
resource "aws_glue_job" "project-2-ecdc-job" {
  name     = "project-2-ecdc-job"
  role_arn = aws_iam_role.glue_exec.arn

  command {
    name            = "glueetl"
    script_location = "s3://project-2-air-health-data-platform/scripts/project-2-ecdc-job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                    = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                   = "true"
  }

  glue_version = "4.0"
  worker_type  = "G.1X"
  number_of_workers = 2
  timeout      = 10
  max_retries  = 1

  tags = var.default_tags
}

# Eurostat Glue Job
resource "aws_glue_job" "project-2-eurostat-job" {
  name     = "project-2-eurostat-job"
  role_arn = aws_iam_role.glue_exec.arn

  command {
    name            = "glueetl"
    script_location = "s3://project-2-air-health-data-platform/scripts/project-2-eurostat-job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                    = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                   = "true"
  }

  glue_version = "4.0"
  worker_type  = "G.1X"
  number_of_workers = 2
  timeout      = 10
  max_retries  = 1

  tags = var.default_tags
}

# Openaq Glue Job
resource "aws_glue_job" "project-2-openaq-job" {
  name     = "project-2-openaq-job"
  role_arn = aws_iam_role.glue_exec.arn

  command {
    name            = "glueetl"
    script_location = "s3://project-2-air-health-data-platform/scripts/project-2-openaq-job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                    = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                   = "true"
  }

  glue_version = "4.0"
  worker_type  = "G.1X"
  number_of_workers = 2
  timeout      = 10
  max_retries  = 1

  tags = var.default_tags
}

# WHO Glue Job
resource "aws_glue_job" "project-2-who-job" {
  name     = "project-2-who-job"
  role_arn = aws_iam_role.glue_exec.arn

  command {
    name            = "glueetl"
    script_location = "s3://project-2-air-health-data-platform/scripts/project-2-who-job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                    = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                   = "true"
  }

  glue_version = "4.0"
  worker_type  = "G.1X"
  number_of_workers = 2
  timeout      = 10
  max_retries  = 1

  tags = var.default_tags
}
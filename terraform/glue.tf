# AWS Glue Database
resource "aws_glue_catalog_database" "bronze_db" {
  name        = "air_health_bronze"
  description = "Glue database for raw (bronze) air quality and health data"
}

# AWS Glue Crawlers
resource "aws_glue_crawler" "openaq" {
  name          = "project2-openaq-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.bronze_db.name

  s3_target {
    path = "s3://${var.s3_bucket_name}/bronze/openaq/v3/eu27"
  }
}

resource "aws_glue_crawler" "who" {
  name          = "project2-who-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.bronze_db.name

  s3_target {
    path = "s3://${var.s3_bucket_name}/bronze/who/"
  }
}

resource "aws_glue_crawler" "ecdc" {
  name          = "project2-ecdc-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.bronze_db.name

  s3_target {
    path = "s3://${var.s3_bucket_name}/bronze/ecdc/"
  }
}

resource "aws_glue_crawler" "eurostat" {
  name          = "project2-eurostat-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.bronze_db.name

  s3_target {
    path = "s3://${var.s3_bucket_name}/bronze/eurostat/"
  }
}

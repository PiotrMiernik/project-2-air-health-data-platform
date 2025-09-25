# Outputs for S3
output "s3_bucket_name" {
  description = "Name of the S3 bucket for the data lake"
  value       = aws_s3_bucket.data_lake.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for the data lake"
  value       = aws_s3_bucket.data_lake.arn
}

# Outputs for Lambda IAM Role
output "lambda_role_name" {
  description = "Name of the IAM role for Lambda execution"
  value       = aws_iam_role.lambda_role.name
}

output "lambda_role_arn" {
  description = "ARN of the IAM role for Lambda execution"
  value       = aws_iam_role.lambda_role.arn
}

# Outputs for CI/CD User
output "cicd_user_name" {
  description = "Name of the IAM user for GitHub Actions (CI/CD)"
  value       = aws_iam_user.cicd_user.name
}

output "cicd_user_arn" {
  description = "ARN of the IAM user for GitHub Actions (CI/CD)"
  value       = aws_iam_user.cicd_user.arn
}

# Glue Outputs
output "glue_bronze_db_name" {
  description = "Name of the Glue database for Bronze layer"
  value       = aws_glue_catalog_database.bronze_db.name
}

output "glue_crawlers" {
  description = "List of Glue crawler names"
  value = [
    aws_glue_crawler.openaq.name,
    aws_glue_crawler.who.name,
    aws_glue_crawler.ecdc.name,
    aws_glue_crawler.eurostat.name
  ]
}

output "glue_service_role_arn" {
  description = "IAM Role ARN used by Glue"
  value       = aws_iam_role.glue_service_role.arn
}

# Athena Outputs
output "athena_workgroup_name" {
  description = "Athena workgroup for queries"
  value       = aws_athena_workgroup.project2.name
}

output "athena_databases" {
  description = "Athena databases for Bronze, Silver, Gold layers"
  value = [
    aws_athena_database.bronze.name,
    aws_athena_database.silver.name,
    aws_athena_database.gold.name
  ]
}

output "athena_results_location" {
  description = "S3 location where Athena stores query results"
  value       = aws_athena_workgroup.project2.configuration[0].result_configuration[0].output_location
}

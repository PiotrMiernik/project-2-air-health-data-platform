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

# --- GLUE Outputs ---
output "glue_silver_db_name" {
  description = "Name of the Glue database for Silver layer"
  value       = aws_glue_catalog_database.silver_db.name
}

output "glue_gold_db_name" {
  description = "Name of the Glue database for Gold layer"
  value       = aws_glue_catalog_database.gold_db.name
}

output "glue_service_role_arn" {
  description = "IAM Role ARN used by Glue"
  value       = aws_iam_role.glue_service_role.arn
}

output "glue_crawlers_silver" {
  description = "List of all Glue crawler names for the Silver layer"
  value       = [
    aws_glue_crawler.ecdc_silver.name,
    aws_glue_crawler.who_silver.name,
    aws_glue_crawler.eurostat_silver.name,
    aws_glue_crawler.openaq_silver.name
  ]
}

# --- ATHENA Outputs ---
output "athena_workgroup_name" {
  description = "Athena workgroup for queries"
  value       = aws_athena_workgroup.project2.name
}

output "athena_results_location" {
  description = "S3 location where Athena stores query results"
  value       = aws_athena_workgroup.project2.configuration[0].result_configuration[0].output_location
}

# --- ORCHESTRATION (Step Functions) Outputs ---
output "sfn_state_machine_arn" {
  description = "ARN of the main Step Functions State Machine for ETL orchestration"
  value       = aws_sfn_state_machine.air_health_platform_orchestration.arn
}

output "sfn_state_machine_name" {
  description = "Name of the Step Functions State Machine"
  value       = aws_sfn_state_machine.air_health_platform_orchestration.name
}
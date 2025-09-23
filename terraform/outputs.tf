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

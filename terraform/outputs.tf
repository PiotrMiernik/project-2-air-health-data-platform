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
output "lambda_exec_role_name" {
  description = "Name of the IAM role for Lambda execution"
  value       = aws_iam_role.lambda_exec_role.name
}

output "lambda_exec_role_arn" {
  description = "ARN of the IAM role for Lambda execution"
  value       = aws_iam_role.lambda_exec_role.arn
}

# Outputs for CI/CD User
output "ci_user_name" {
  description = "Name of the IAM user for GitHub Actions (CI/CD)"
  value       = aws_iam_user.ci_user.name
}

output "ci_user_arn" {
  description = "ARN of the IAM user for GitHub Actions (CI/CD)"
  value       = aws_iam_user.ci_user.arn
}

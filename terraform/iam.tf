
# IAM role for AWS Lambda (data ingestion)
resource "aws_iam_role" "lambda_role" {
  name = "project2-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.default_tags
}

# IAM policy for Lambda: allow S3 access and CloudWatch logging
resource "aws_iam_policy" "lambda_policy" {
  name        = "project2-lambda-policy"
  description = "Policy that allows Lambda to access S3 and log to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach the policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# IAM role for CI/CD (GitHub Actions)
resource "aws_iam_role" "cicd_role" {
  name = "project2-cicd-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "*" 
        }
      }
    ]
  })

  tags = var.default_tags
}

# IAM policy for CI/CD: allow deploy and S3 operations
resource "aws_iam_policy" "cicd_policy" {
  name        = "project2-cicd-policy"
  description = "Policy for CI/CD pipeline to deploy Lambda and manage S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "lambda:*",
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach the policy to the CI/CD role
resource "aws_iam_role_policy_attachment" "cicd_attach" {
  role       = aws_iam_role.cicd_role.name
  policy_arn = aws_iam_policy.cicd_policy.arn
}

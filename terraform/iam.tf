# IAM role for AWS Lambda (data ingestion functions)
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

# IAM user for CI/CD (GitHub Actions)
resource "aws_iam_user" "cicd_user" {
  name = "github_actions_user_project2"
  tags = var.default_tags
}

resource "aws_iam_user_policy" "cicd_user_policy" {
  name = "project2-cicd-user-policy"
  user = aws_iam_user.cicd_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "lambda:*",
          "iam:PassRole",
          "cloudwatch:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM role for AWS Step Functions
resource "aws_iam_role" "stepfunction_exec_role" {
  name = "project2-stepfunction-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.default_tags
}

# IAM policy for Step Functions
resource "aws_iam_role_policy" "stepfunction_policy" {
  name = "project2-stepfunction-policy"
  role = aws_iam_role.stepfunction_exec_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["lambda:InvokeFunction"]
        Resource = [
          aws_lambda_function.api_ingestion["openaq"].arn,
          aws_lambda_function.api_ingestion["who"].arn,
          aws_lambda_function.api_ingestion["ecdc"].arn,
          aws_lambda_function.api_ingestion["eurostat"].arn
        ]
      }
    ]
  })
}

# IAM role for AWS EventBridge
resource "aws_iam_role" "eventbridge_invoke_stepfn_role" {
  name = "project2-eventbridge-invoke-stepfn-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.default_tags
}

# IAM policy for EventBridge
resource "aws_iam_role_policy" "eventbridge_invoke_stepfn_policy" {
  name = "project2-eventbridge-invoke-stepfn-policy"
  role = aws_iam_role.eventbridge_invoke_stepfn_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "states:StartExecution"
      ]
      Resource = aws_sfn_state_machine.orchestration.arn
    }]
  })
}

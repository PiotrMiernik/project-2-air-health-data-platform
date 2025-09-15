resource "aws_lambda_function" "api_ingestion" {
  for_each = var.lambda_functions

  function_name = "project2-${each.key}-lambda"
  role          = aws_iam_role.lambda_role.arn
  runtime       = each.value.runtime
  handler       = each.value.handler

  # Wskazanie paczki ZIP wrzuconej wcześniej do S3
  s3_bucket = aws_s3_bucket.data_lake.bucket
  s3_key    = each.value.s3_key

  environment {
    variables = each.value.env_vars
  }

  tags = var.default_tags
}
resource "aws_lambda_function" "api_ingestion" {
  for_each = var.lambda_functions

  function_name = "project2-${each.key}-lambda"
  role          = aws_iam_role.lambda_role.arn
  runtime       = each.value.runtime
  handler       = each.value.handler

  # Obsługa dwóch wariantów: kod w S3 albo lokalny ZIP
  s3_bucket = lookup(each.value, "s3_bucket", null)
  s3_key    = lookup(each.value, "s3_key", null)

  filename         = lookup(each.value, "filename", null)
  source_code_hash = lookup(each.value, "filename", null) != null ? filebase64sha256(each.value.filename) : null

  timeout     = lookup(each.value, "timeout", 3)
  memory_size = lookup(each.value, "memory_size", 128)

  environment {
    variables = merge(
      each.value.env_vars,
      each.key == "openaq" ? { OPENAQ_API_KEY = var.openaq_api_key } : {}
    )
  }

  tags = var.default_tags
}

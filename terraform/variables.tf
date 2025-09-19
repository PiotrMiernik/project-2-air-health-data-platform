# AWS region in which resources will be deployed
variable "aws_region" {
  description = "AWS region for deploying infrastructure"
  type        = string
}

# Name of the main S3 bucket for the data lake
variable "s3_bucket_name" {
  description = "Main S3 bucket that stores the data lake layers (bronze/silver/gold)"
  type        = string
}

# Tags applied to all resources
variable "default_tags" {
  description = "Default tags applied to all resources"
  type        = map(string)
}

# Definition of Lambda functions
variable "lambda_functions" {
  description = "Lambda functions for API ingestion"
  type = map(object({
    handler     = string
    runtime     = string
    s3_bucket   = optional(string)
    s3_key      = optional(string)
    filename    = optional(string)
    timeout     = optional(number)
    memory_size = optional(number)
    env_vars    = map(string)
  }))
}

variable "openaq_api_key" {
  description = "OpenAQ v3 API key"
  type        = string
  sensitive   = true
}

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

# Prefix for the raw data (bronze layer)
variable "bronze_prefix" {
  description = "Prefix (folder path) for raw data in the bronze layer"
  type        = string
  default     = "bronze/"
}

# Prefix for the cleaned/staged data (silver layer)
variable "silver_prefix" {
  description = "Prefix (folder path) for processed data in the silver layer"
  type        = string
  default     = "silver/"
}

# Prefix for the analytical/curated data (gold layer)
variable "gold_prefix" {
  description = "Prefix (folder path) for final analytical data in the gold layer"
  type        = string
  default     = "gold/"
}

# Tags applied to all resources (good practice in AWS for cost tracking and ownership)
variable "default_tags" {
  description = "Default tags applied to all resources (e.g., project, owner)"
  type        = map(string)
  default = {
    Project = "Air Health Data Platform"
    Owner   = "Piotr Miernik"
  }
}

variable "lambda_functions" {
  description = "Lambda functions for API ingestion"
  type = map(object({
    handler  = string
    runtime  = string
    s3_key   = string
    env_vars = map(string)
  }))

  default = {
    ecdc = {
      handler   = "download_ecdc.lambda_handler"
      runtime   = "python3.11"
      s3_key    = "lambda/ecdc.zip"
      env_vars  = {
        API_NAME  = "ECDC"
        S3_BUCKET = "project-2-air-health-data-platform"
        S3_PREFIX = "bronze/ecdc/"
      }
    }
    eurostat = {
      handler   = "download_eurostat.lambda_handler"
      runtime   = "python3.11"
      s3_key    = "lambda/eurostat.zip"
      env_vars  = {
        API_NAME  = "Eurostat"
        S3_BUCKET = "project-2-air-health-data-platform"
        S3_PREFIX = "bronze/eurostat/"
      }
    }
    openaq = {
      handler   = "download_openaq.lambda_handler"
      runtime   = "python3.11"
      s3_key    = "lambda/openaq.zip"
      env_vars  = {
        API_NAME  = "OpenAQ"
        S3_BUCKET = "project-2-air-health-data-platform"
        S3_PREFIX = "bronze/openaq/"
      }
    }
    who = {
      handler   = "download_who.lambda_handler"
      runtime   = "python3.11"
      s3_key    = "lambda/who.zip"
      env_vars  = {
        API_NAME  = "WHO"
        S3_BUCKET = "project-2-air-health-data-platform"
        S3_PREFIX = "bronze/who/"
      }
    }
  }
}


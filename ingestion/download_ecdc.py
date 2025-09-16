import os
import json
import boto3
import requests
from botocore.exceptions import ClientError

# ECDC national cases & deaths dataset (country-level, JSON)
ECDC_COVID_URL = "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath/json/"

# Environment variables (set via Terraform)
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/ecdc/")

# AWS S3 client
s3_client = boto3.client("s3")


def fetch_ecdc_covid_data():
    """
    Fetch COVID-19 cases and deaths data from the ECDC API.
    Returns:
        dict: JSON response with records by country and date
    """
    response = requests.get(ECDC_COVID_URL, timeout=60)
    response.raise_for_status()
    return response.json()


def save_to_s3(data: dict, key: str):
    """
    Save raw JSON data to S3 bronze layer.
    Args:
        data (dict): The dataset to store
        key (str): Target S3 object key
    """
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
    except ClientError as e:
        raise RuntimeError(f"Failed to upload to S3: {e}")


def lambda_handler(event, context):
    """
    AWS Lambda handler.
    Extracts COVID-19 national cases/deaths data from ECDC and stores it in S3 (bronze).
    """
    data = fetch_ecdc_covid_data()

    # Unique file name: use request ID
    output_key = f"{S3_PREFIX}ecdc_covid_{context.aws_request_id}.json"

    save_to_s3(data, output_key)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "ECDC COVID-19 data successfully fetched and stored in S3 (bronze)",
            "s3_key": output_key
        })
    }

import os
import json
import boto3
import requests
from botocore.exceptions import ClientError

# Eurostat API base URL
EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# Selected Eurostat datasets
EUROSTAT_DATASETS = {
    "hlth_cd_aro": "Deaths from respiratory diseases",
    "env_air_gge": "Greenhouse gas emissions",
    "nama_10_pc": "GDP per capita (PPS)",
    "ilc_mdho06a": "Severe housing deprivation rate",
}

# EU27 ISO2 codes (Eurostat standard)
EU27_COUNTRIES = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE"
]

# Environment variables (set via Terraform)
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/eurostat/")

# AWS S3 client
s3_client = boto3.client("s3")


def fetch_eurostat_dataset(dataset_code: str, country_code: str) -> dict:
    """
    Fetch Eurostat dataset for a single EU27 country.
    Args:
        dataset_code (str): Eurostat dataset code
        country_code (str): ISO2 code of the country
    Returns:
        dict: JSON response from Eurostat
    """
    url = f"{EUROSTAT_BASE_URL}/{dataset_code}?lang=EN&geo={country_code}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def save_to_s3(data: dict, dataset_code: str, country_code: str, request_id: str):
    """
    Save JSON dataset to S3 bronze zone.
    Args:
        data (dict): Dataset to store
        dataset_code (str): Eurostat dataset code
        country_code (str): ISO2 code of the country
        request_id (str): Lambda request ID
    """
    key = f"{S3_PREFIX}{dataset_code}/{country_code}_{request_id}.json"
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
    except ClientError as e:
        raise RuntimeError(f"Failed to upload {dataset_code} ({country_code}) to S3: {e}")
    return key


def lambda_handler(event, context):
    """
    AWS Lambda handler.
    Fetches selected Eurostat datasets for all EU27 countries and stores them in S3 bronze layer.
    """
    stored_keys = {}

    for dataset_code, description in EUROSTAT_DATASETS.items():
        stored_keys[dataset_code] = []
        for country in EU27_COUNTRIES:
            data = fetch_eurostat_dataset(dataset_code, country)
            key = save_to_s3(data, dataset_code, country, context.aws_request_id)
            stored_keys[dataset_code].append(key)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Eurostat datasets (EU27) successfully fetched and stored in S3 (bronze)",
            "stored_files": stored_keys
        })
    }

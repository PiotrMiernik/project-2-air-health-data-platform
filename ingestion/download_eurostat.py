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

# EU27 ISO2 codes
EU27_COUNTRIES = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE"
]

# Environment variables
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/eurostat/")

s3_client = boto3.client("s3")


def fetch_eurostat_dataset(dataset_code: str, country_code: str) -> dict:
    """
    Fetch Eurostat dataset for a single EU27 country with simplified dimensions.
    Filters out unnecessary breakdowns (sex, age, unit) to reduce payload size.
    """
    # Apply simple filters for total/aggregated data
    if dataset_code == "hlth_cd_aro":
        url = f"{EUROSTAT_BASE_URL}/{dataset_code}?lang=EN&geo={country_code}&sex=T&unit=RT"
    else:
        url = f"{EUROSTAT_BASE_URL}/{dataset_code}?lang=EN&geo={country_code}"

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 413:
            print(f"Skipping {dataset_code} for {country_code}: payload too large")
            return None
        else:
            raise


def save_to_s3(data: dict, dataset_code: str, country_code: str, request_id: str):
    """Save JSON dataset to S3 (bronze layer)."""
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
    """AWS Lambda handler: fetch selected Eurostat datasets per country."""
    stored_keys = {}

    for dataset_code, description in EUROSTAT_DATASETS.items():
        stored_keys[dataset_code] = []
        for country in EU27_COUNTRIES:
            data = fetch_eurostat_dataset(dataset_code, country)
            if not data:
                continue  # skip if request failed or too large
            key = save_to_s3(data, dataset_code, country, context.aws_request_id)
            stored_keys[dataset_code].append(key)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Eurostat datasets (EU27, aggregated) successfully fetched and stored in S3 (bronze)",
            "stored_files": stored_keys
        })
    }

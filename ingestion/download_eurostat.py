import os
import json
import boto3
import requests
from botocore.exceptions import ClientError

# Eurostat API base URL
EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# Relevant Eurostat datasets
EUROSTAT_DATASETS = {
    # Health and Environment
    "hlth_cd_aro": "Deaths from respiratory diseases",
    "hlth_cd_asdr2": "Standardised death rate by cause",
    "env_air_emis": "Air pollutant emissions by source sector",
    "env_ac_ainah_r2": "Air emissions accounts by NACE Rev.2 activity",
    "env_air_gge": "Greenhouse gas emissions",
    # Socio-economic
    "nama_10_pc": "GDP per capita (PPS)",
    "ilc_di12": "Gini coefficient of income inequality",
    "ilc_li02": "At-risk-of-poverty rate",
    "edat_lfse_03": "Educational attainment (ISCED levels)",
    "hlth_silc_08": "Unmet need for medical examination",
    "ilc_lvho05a": "Overcrowding rate",
    "ilc_mdho06a": "Severe housing deprivation rate",
}

# Environment variables (set via Terraform)
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/eurostat/")

# AWS S3 client
s3_client = boto3.client("s3")


def fetch_eurostat_dataset(dataset_code: str) -> dict:
    """
    Fetch a dataset from Eurostat API (JSON-stat).
    Args:
        dataset_code (str): Eurostat dataset code
    Returns:
        dict: JSON response from Eurostat
    """
    url = f"{EUROSTAT_BASE_URL}/{dataset_code}?lang=EN&geo=EU27_2020"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def save_to_s3(data: dict, dataset_code: str, request_id: str):
    """
    Save JSON dataset to S3 bronze zone.
    Args:
        data (dict): The dataset to store
        dataset_code (str): Eurostat dataset code
        request_id (str): Lambda request ID for unique filenames
    """
    key = f"{S3_PREFIX}{dataset_code}_{request_id}.json"
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
    except ClientError as e:
        raise RuntimeError(f"Failed to upload {dataset_code} to S3: {e}")
    return key


def lambda_handler(event, context):
    """
    AWS Lambda handler.
    Extracts all 5 Eurostat datasets and stores them in S3 bronze layer.
    """
    stored_keys = {}

    for dataset_code, description in EUROSTAT_DATASETS.items():
        data = fetch_eurostat_dataset(dataset_code)
        key = save_to_s3(data, dataset_code, context.aws_request_id)
        stored_keys[dataset_code] = key

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Eurostat datasets successfully fetched and stored in S3 (bronze)",
            "stored_files": stored_keys
        })
    }

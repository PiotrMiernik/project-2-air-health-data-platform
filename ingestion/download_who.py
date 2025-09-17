import os
import json
import boto3
import requests
from botocore.exceptions import ClientError

# WHO GHO API base URL
WHO_BASE_URL = "https://ghoapi.azureedge.net/api"

# Selected WHO indicators for project
WHO_INDICATORS = {
    # Air pollution and health
    "AIR_10": "Ambient air pollution attributable DALYs per 100k children under 5",
    "AIR_12": "Household air pollution attributable deaths in children under 5",
    "AIR_15": "Household air pollution attributable DALYs",
    "AIR_16": "Household air pollution attributable DALYs in children under 5",
    "AIR_35": "Joint effects of air pollution attributable deaths",
    "AIR_42": "Ambient air pollution attributable death rate (per 100k, age-standardized)",
    "AIR_46": "YLLs attributable to ambient air pollution (age-standardized)",
    "AIR_6": "Ambient air pollution attributable deaths per 100k children under 5",
    "AIR_60": "Household and ambient air pollution attributable DALYs",
    "AIR_62": "Household and ambient air pollution attributable DALYs (per 100k, age-standardized)",
    # Other health/environment indicators
    "MORT_500": "Number of deaths",
    "MORT_700": "Projection of deaths per 100k population",
    "TOTENV_3": "DALYs attributable to the environment",
    "TOTENV_90": "Total environment attributable DALYs in children under 5",
}

# List of EU27 ISO country codes (WHO uses ISO2/ISO3 codes, here we assume ISO2)
EU27_COUNTRIES = EU27_COUNTRIES = [
    "AUT",  # Austria
    "BEL",  # Belgium
    "BGR",  # Bulgaria
    "HRV",  # Croatia
    "CYP",  # Cyprus
    "CZE",  # Czechia
    "DNK",  # Denmark
    "EST",  # Estonia
    "FIN",  # Finland
    "FRA",  # France
    "DEU",  # Germany
    "GRC",  # Greece
    "HUN",  # Hungary
    "IRL",  # Ireland
    "ITA",  # Italy
    "LVA",  # Latvia
    "LTU",  # Lithuania
    "LUX",  # Luxembourg
    "MLT",  # Malta
    "NLD",  # Netherlands
    "POL",  # Poland
    "PRT",  # Portugal
    "ROU",  # Romania
    "SVK",  # Slovakia
    "SVN",  # Slovenia
    "ESP",  # Spain
    "SWE",  # Sweden
]

# Environment variables (set in Terraform)
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/who/")

# AWS S3 client
s3_client = boto3.client("s3")


def fetch_who_indicator(indicator_code: str) -> dict:
    """
    Fetch WHO indicator data from API for EU27 countries.
    Args:
        indicator_code (str): WHO Indicator code
    Returns:
        dict: JSON response from WHO API
    """
    url = f"{WHO_BASE_URL}/{indicator_code}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()

    # Filter only EU countries and yearly records
    filtered_records = [
        rec for rec in data.get("value", [])
        if rec.get("SpatialDim") in EU27_COUNTRIES and rec.get("TimeDimType") == "YEAR"
    ]

    return {"indicator": indicator_code, "records": filtered_records}


def save_to_s3(data: dict, indicator_code: str, request_id: str):
    """
    Save WHO dataset to S3 as JSON.
    Args:
        data (dict): Filtered WHO dataset
        indicator_code (str): WHO indicator code
        request_id (str): Lambda request ID
    """
    key = f"{S3_PREFIX}{indicator_code}_{request_id}.json"
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
    except ClientError as e:
        raise RuntimeError(f"Failed to upload {indicator_code} to S3: {e}")
    return key


def lambda_handler(event, context):
    """
    AWS Lambda handler.
    Fetches all WHO indicators and stores them in S3 bronze layer.
    """
    stored_keys = {}

    for indicator_code, description in WHO_INDICATORS.items():
        data = fetch_who_indicator(indicator_code)
        key = save_to_s3(data, indicator_code, context.aws_request_id)
        stored_keys[indicator_code] = key

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "WHO indicators successfully fetched and stored in S3 (bronze)",
            "stored_files": stored_keys
        })
    }

import os
import json
import boto3
import requests
from datetime import datetime
from botocore.exceptions import ClientError

# OpenAQ API base URLs
OPENAQ_MEASUREMENTS_URL = "https://api.openaq.org/v2/measurements"
OPENAQ_LOCATIONS_URL = "https://api.openaq.org/v2/locations"

# List of EU27 ISO2 country codes
EU27_COUNTRIES = [
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE",
    "GR","HU","IE","IT","LV","LT","LU","MT","NL","PL",
    "PT","RO","SK","SI","ES","SE"
]

# Max locations per country (custom rules)
COUNTRY_LOCATIONS_LIMIT = {
    "LU": 1, "MT": 1, "EE": 2, "LV": 2, "CY": 2,
    "HR": 3, "SI": 3, "SK": 3, "BG": 3, "LT": 3,
    "AT": 5, "BE": 5, "CZ": 5, "DK": 5, "FI": 5,
    "GR": 5, "HU": 5, "IE": 5, "NL": 5, "PT": 5, "SE": 5,
    "PL": 8, "ES": 8, "IT": 8,
    "FR": 10, "DE": 10
}

# Pollutants of interest
POLLUTANTS = ["pm25", "pm10", "no2", "o3", "co", "so2"]

# Date range
DATE_FROM = "2014-01-01"
DATE_TO = datetime.utcnow().strftime("%Y-%m-%d")

# Environment variables (Terraform will set them)
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/openaq/")

# AWS S3 client
s3_client = boto3.client("s3")


def get_top_locations(country_code: str, limit: int):
    """
    Fetch top locations (cities/stations) for a given country from OpenAQ.
    Sort by number of measurements (descending).
    """
    params = {
        "country": country_code,
        "limit": limit,
        "sort": "desc",
        "order_by": "count"
    }
    response = requests.get(OPENAQ_LOCATIONS_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    # Return only up to 'limit' items
    return [loc["id"] for loc in data.get("results", [])[:limit]]


def fetch_openaq_data(country_code: str, location_ids: list):
    """
    Fetch daily measurements for selected pollutants in chosen locations.
    """
    records = []

    for loc_id in location_ids:
        params = {
            "country": country_code,
            "location_id": loc_id,
            "date_from": DATE_FROM,
            "date_to": DATE_TO,
            "temporal": "day",
            "parameter": POLLUTANTS,
            "limit": 10000,
            "sort": "desc"
        }
        response = requests.get(OPENAQ_MEASUREMENTS_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        records.extend(data.get("results", []))

    return {"country": country_code, "records": records}


def save_to_s3(data: dict, country_code: str, request_id: str):
    """
    Save data to S3 as JSON.
    """
    key = f"{S3_PREFIX}{country_code}_{request_id}.json"
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
    except ClientError as e:
        raise RuntimeError(f"Failed to upload OpenAQ data for {country_code}: {e}")
    return key


def lambda_handler(event, context):
    """
    AWS Lambda handler.
    Fetches OpenAQ data for EU27 countries and stores in S3.
    """
    stored_keys = {}

    for country_code in EU27_COUNTRIES:
        limit = COUNTRY_LOCATIONS_LIMIT.get(country_code, 3)

        # Step 1: Get top locations by activity
        location_ids = get_top_locations(country_code, limit)

        # Step 2: Fetch measurements from those locations
        data = fetch_openaq_data(country_code, location_ids)

        # Step 3: Save to S3
        key = save_to_s3(data, country_code, context.aws_request_id)
        stored_keys[country_code] = key

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "OpenAQ data successfully fetched and stored in S3 (bronze)",
            "stored_files": stored_keys
        })
    }

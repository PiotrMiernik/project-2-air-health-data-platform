import os
import json
import time
import boto3
import requests
from io import BytesIO
from datetime import datetime, timezone

# === OpenAQ API v3 ===
OPENAQ_API_URL = "https://api.openaq.org/v3/measurements"
API_KEY = os.environ.get("OPENAQ_API_KEY")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

# Only PM2.5
POLLUTANT_NAME = "pm25"
POLLUTANT_ID = 2

# Time range: from 2024-01-01 to now
DATE_FROM = "2024-01-01"
DATE_TO = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# EU27 ISO country codes
EU27_COUNTRIES = [
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR",
    "HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK",
    "SI","ES","SE"
]

# Top cities per country
TOP_CITIES_BY_COUNTRY = {
    "AT": ["Vienna"], "BE": ["Brussels"], "BG": ["Sofia"], "HR": ["Zagreb"],
    "CY": ["Nicosia"], "CZ": ["Prague"], "DK": ["Copenhagen"], "EE": ["Tallinn"],
    "FI": ["Helsinki"], "FR": ["Paris", "Marseille", "Lyon"],
    "DE": ["Berlin", "Hamburg", "Munich"], "GR": ["Athens"], "HU": ["Budapest"],
    "IE": ["Dublin"], "IT": ["Rome", "Milan"], "LV": ["Riga"], "LT": ["Vilnius"],
    "LU": ["Luxembourg"], "MT": ["Valletta"], "NL": ["Amsterdam"],
    "PL": ["Warsaw", "Krakow"], "PT": ["Lisbon"], "RO": ["Bucharest"],
    "SK": ["Bratislava"], "SI": ["Ljubljana"], "ES": ["Madrid", "Barcelona"],
    "SE": ["Stockholm"],
}

# AWS S3
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/openaq/v3/eu27/")
s3 = boto3.client("s3")


def _request(params, retries=3, backoff=1.5):
    """Helper to call OpenAQ API with retry on 429."""
    for attempt in range(retries):
        r = requests.get(OPENAQ_API_URL, headers=HEADERS, params=params, timeout=60)
        if r.status_code == 429:
            time.sleep(backoff * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def save_json_to_s3(obj: dict, key: str):
    """Save JSON object to S3."""
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=BytesIO(json.dumps(obj, ensure_ascii=False).encode("utf-8")),
        ContentType="application/json",
    )


def fetch_city_data(iso: str, city: str, request_id: str):
    """Fetch all PM2.5 measurements for a city and save to S3."""
    page = 1
    total_found = None
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    while True:
        params = {
            "iso": iso,
            "city": city,
            "parameter_id": POLLUTANT_ID,
            "datetime_from": DATE_FROM,
            "datetime_to": DATE_TO,
            "limit": 1000,
            "page": page,
        }
        data = _request(params=params)
        meta = data.get("meta", {})
        found = meta.get("found", 0)
        limit = meta.get("limit", 1000)

        total_found = found if total_found is None else total_found
        key = f"{S3_PREFIX}{iso}/{city.lower().replace(' ', '-')}/{POLLUTANT_NAME}/page={page}_{request_id}_{ts}.json"
        save_json_to_s3(data, key)

        if page * limit >= found or found == 0:
            break
        page += 1

    return total_found or 0


def lambda_handler(event, context):
    if not S3_BUCKET:
        return {"statusCode": 500, "body": json.dumps({"error": "Missing S3_BUCKET env"})}
    if not API_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "Missing OPENAQ_API_KEY env"})}

    stored = {}
    for iso in EU27_COUNTRIES:
        for city in TOP_CITIES_BY_COUNTRY.get(iso, []):
            try:
                n_records = fetch_city_data(iso, city, context.aws_request_id if context else "local")
                stored[f"{iso}:{city}"] = f"OK: records={n_records}"
            except Exception as e:
                stored[f"{iso}:{city}"] = f"ERROR: {str(e)}"

    return {
        "statusCode": 200,
        "body": json.dumps({"stored": stored}, ensure_ascii=False)
    }

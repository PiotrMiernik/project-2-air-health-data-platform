import os
import json
import boto3
import pytest
from moto import mock_aws
from ingestion import download_who


@pytest.fixture(scope="function")
def aws_env(monkeypatch):
    """Set environment variables for S3 bucket and prefix."""
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("S3_PREFIX", "bronze/who/")


@pytest.fixture(scope="function")
def s3_client_mock():
    """Mocked S3 client using moto."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-central-1")
        s3.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-central-1"},
        )
        yield s3


def test_fetch_who_indicator_filters_only_eu(requests_mock):
    """Test fetching WHO indicator returns only EU countries and yearly data."""
    mock_data = {
        "value": [
            {"IndicatorCode": "AIR_10", "SpatialDim": "PL", "TimeDimType": "YEAR", "Value": 123},
            {"IndicatorCode": "AIR_10", "SpatialDim": "US", "TimeDimType": "YEAR", "Value": 456},
            {"IndicatorCode": "AIR_10", "SpatialDim": "DE", "TimeDimType": "MONTH", "Value": 789},
        ]
    }
    url = f"{download_who.WHO_BASE_URL}/AIR_10"
    requests_mock.get(url, json=mock_data, status_code=200)

    result = download_who.fetch_who_indicator("AIR_10")
    records = result["records"]

    assert result["indicator"] == "AIR_10"
    assert all(rec["SpatialDim"] in download_who.EU27_COUNTRIES for rec in records)
    assert all(rec["TimeDimType"] == "YEAR" for rec in records)


def test_lambda_handler_fetches_all(aws_env, s3_client_mock, requests_mock):
    """Test full Lambda handler: fetch all WHO indicators → save → return keys."""
    # Mock all WHO indicators with minimal EU data
    for indicator_code in download_who.WHO_INDICATORS.keys():
        url = f"{download_who.WHO_BASE_URL}/{indicator_code}"
        requests_mock.get(url, json={
            "value": [
                {"IndicatorCode": indicator_code, "SpatialDim": "PL", "TimeDimType": "YEAR", "Value": 1}
            ]
        }, status_code=200)

    # Patch boto3 client
    download_who.s3_client = s3_client_mock
    # Override env vars inside module
    download_who.S3_BUCKET = "test-bucket"
    download_who.S3_PREFIX = "bronze/who/"

    # Fake Lambda context
    class Context:
        aws_request_id = "9999"

    response = download_who.lambda_handler({}, Context())

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert "stored_files" in body
    assert len(body["stored_files"]) == len(download_who.WHO_INDICATORS)

    # Verify that each indicator was stored in S3
    for indicator_code, key in body["stored_files"].items():
        obj = s3_client_mock.get_object(Bucket="test-bucket", Key=key)
        stored_data = json.loads(obj["Body"].read().decode("utf-8"))
        assert stored_data["indicator"] == indicator_code
        assert "records" in stored_data

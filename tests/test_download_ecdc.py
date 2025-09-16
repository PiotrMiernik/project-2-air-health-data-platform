import os
import json
import boto3
import pytest
from moto import mock_aws
from ingestion import download_ecdc


@pytest.fixture(scope="function")
def aws_env(monkeypatch):
    """Set environment variables for S3 bucket and prefix."""
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("S3_PREFIX", "bronze/ecdc/")


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


def test_fetch_ecdc_covid_data(requests_mock):
    """Test that data is fetched correctly from the ECDC API."""
    mock_data = [{"country": "Poland", "cases": 100, "deaths": 5}]
    requests_mock.get(download_ecdc.ECDC_COVID_URL, json=mock_data, status_code=200)

    result = download_ecdc.fetch_ecdc_covid_data()
    assert result == mock_data
    assert isinstance(result, list)


def test_save_to_s3_and_lambda_handler(aws_env, s3_client_mock, requests_mock):
    """Test the full Lambda handler flow: fetch → save → return."""
    # Mock API response
    mock_data = [{"country": "Germany", "cases": 200, "deaths": 10}]
    requests_mock.get(download_ecdc.ECDC_COVID_URL, json=mock_data, status_code=200)

    # Patch boto3 client to use moto
    download_ecdc.s3_client = s3_client_mock

    # Run handler with fake context
    class Context:
        aws_request_id = "1234"

    download_ecdc.S3_BUCKET = "test-bucket"
    download_ecdc.S3_PREFIX = "bronze/ecdc/"


    response = download_ecdc.lambda_handler({}, Context())

    # Validate Lambda response
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert "s3_key" in body

    # Check file exists in S3
    s3_key = body["s3_key"]
    obj = s3_client_mock.get_object(Bucket="test-bucket", Key=s3_key)
    stored_data = json.loads(obj["Body"].read().decode("utf-8"))

    assert stored_data == mock_data

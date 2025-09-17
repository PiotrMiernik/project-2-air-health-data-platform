import os
import json
import boto3
import pytest
from moto import mock_aws
from ingestion import download_openaq


@pytest.fixture(scope="function")
def aws_env(monkeypatch):
    """Set environment variables for S3 bucket and prefix."""
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("S3_PREFIX", "bronze/openaq/")


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


def test_get_top_locations(requests_mock):
    """Test that get_top_locations returns correct location IDs limited to N."""
    mock_locations = {
        "results": [
            {"id": 101, "name": "Berlin"},
            {"id": 102, "name": "Munich"},
            {"id": 103, "name": "Hamburg"},
        ]
    }
    requests_mock.get(
        download_openaq.OPENAQ_LOCATIONS_URL,
        json=mock_locations,
        status_code=200
    )

    ids = download_openaq.get_top_locations("DE", 2)
    assert ids == [101, 102]


def test_fetch_openaq_data(requests_mock):
    """Test fetching measurements for given location IDs."""
    mock_measurements = {
        "results": [
            {"location": "Berlin", "parameter": "pm25", "value": 12},
            {"location": "Berlin", "parameter": "no2", "value": 25},
        ]
    }
    requests_mock.get(
        download_openaq.OPENAQ_MEASUREMENTS_URL,
        json=mock_measurements,
        status_code=200
    )

    data = download_openaq.fetch_openaq_data("DE", [101])
    assert data["country"] == "DE"
    assert len(data["records"]) == 2
    assert data["records"][0]["parameter"] == "pm25"


def test_lambda_handler_flow(aws_env, s3_client_mock, requests_mock):
    """Test full Lambda handler flow: locations → measurements → save to S3."""
    # Mock locations API
    mock_locations = {"results": [{"id": 101}, {"id": 102}]}
    requests_mock.get(download_openaq.OPENAQ_LOCATIONS_URL, json=mock_locations, status_code=200)

    # Mock measurements API
    mock_measurements = {"results": [{"location": "Berlin", "parameter": "pm25", "value": 10}]}
    requests_mock.get(download_openaq.OPENAQ_MEASUREMENTS_URL, json=mock_measurements, status_code=200)

    # Patch boto3 client
    download_openaq.s3_client = s3_client_mock
    # Override env vars inside module
    download_openaq.S3_BUCKET = "test-bucket"
    download_openaq.S3_PREFIX = "bronze/openaq/"

    # Fake Lambda context
    class Context:
        aws_request_id = "abcd"

    response = download_openaq.lambda_handler({}, Context())
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert "stored_files" in body
    assert isinstance(body["stored_files"], dict)

    # Verify that stored file exists in mocked S3
    for _, key in body["stored_files"].items():
        obj = s3_client_mock.get_object(Bucket="test-bucket", Key=key)
        stored_data = json.loads(obj["Body"].read().decode("utf-8"))
        assert stored_data["country"] in download_openaq.EU27_COUNTRIES
        assert "records" in stored_data
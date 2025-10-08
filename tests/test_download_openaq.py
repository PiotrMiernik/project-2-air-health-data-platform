import os
import json
import boto3
import pytest
from moto import mock_aws
from ingestion import download_openaq


@pytest.fixture(scope="function")
def aws_env(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("S3_PREFIX", "bronze/openaq/")
    monkeypatch.setenv("OPENAQ_API_KEY", "fake-api-key")


@pytest.fixture(scope="function")
def s3_client_mock():
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-central-1")
        s3.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-central-1"},
        )
        yield s3


def test_lambda_handler_flow(aws_env, s3_client_mock, monkeypatch):
    """Test Lambda handler flow with mocked _get_json and S3."""

    # --- Mock _get_json to return dummy data for each endpoint ---
    def fake_get_json(url, params=None, **kwargs):
        if url.endswith("/locations"):
            # Return one fake location
            return {"results": [{"id": 1}], "meta": {"found": 1, "limit": 1000}}
        if "/locations/1/sensors" in url:
            # Return one PM2.5 sensor
            return {"results": [{"id": 10, "parameter": {"id": 2}, "coverage": {"observedCount": 100}}]}
        if "/sensors/10/days/yearly" in url:
            # Return fake yearly data
            return {
                "results": [
                    {"year": 2023, "average": 12.3},
                    {"year": 2024, "average": 11.7},
                ],
                "meta": {"found": 2, "limit": 1000},
            }
        return {"results": [], "meta": {"found": 0, "limit": 1000}}

    # Patch _get_json in the module
    monkeypatch.setattr(download_openaq, "_get_json", fake_get_json)

    # Patch boto3 client
    download_openaq.s3 = s3_client_mock
    download_openaq.S3_BUCKET = "test-bucket"
    download_openaq.S3_PREFIX = "bronze/openaq/"

    # Patch API key directly in module
    download_openaq.API_KEY = "fake-api-key"
    download_openaq.HEADERS = {"X-API-Key": "fake-api-key"}

    class Context:
        aws_request_id = "abcd"

    # Run Lambda handler for a single country to simplify
    response = download_openaq.lambda_handler({"countries": ["PL"]}, Context())
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert "stored" in body
    assert isinstance(body["stored"], dict)
    assert "PL" in body["stored"]
    assert "OK" in body["stored"]["PL"] or "WARN" in body["stored"]["PL"]

    # Verify object was written to mock S3
    objects = s3_client_mock.list_objects_v2(Bucket="test-bucket")
    assert "Contents" in objects
    assert len(objects["Contents"]) == 1

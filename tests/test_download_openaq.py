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
    """Test Lambda handler flow with mocked _request and S3."""

    # Mock _request to return dummy data depending on URL
    def fake_request(url, params=None, **kwargs):
        if url.endswith("/locations"):
            return {"results": [{"id": 1, "locality": "Berlin"}], "meta": {"found": 1, "limit": 1000}}
        if "/locations/1/sensors" in url:
            return {"results": [{"id": 10, "parameter": {"id": 2}}]}  # pm25 sensor
        if "/sensors/10/measurements/hourly" in url:
            return {
                "results": [{"coverage": {"observedCount": 100}}],
                "meta": {"found": 1, "limit": 1000}
            }
        return {"results": [], "meta": {"found": 0, "limit": 1000}}

    monkeypatch.setattr(download_openaq, "_request", fake_request)

    # Patch boto3 client
    download_openaq.s3 = s3_client_mock
    download_openaq.S3_BUCKET = "test-bucket"
    download_openaq.S3_PREFIX = "bronze/openaq/"

    # Patch API key directly in module
    download_openaq.API_KEY = "fake-api-key"
    download_openaq.HEADERS = {"X-API-Key": "fake-api-key"}

    class Context:
        aws_request_id = "abcd"

    response = download_openaq.lambda_handler({}, Context())
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert "stored_files" in body
    assert isinstance(body["stored_files"], dict)

    # Verify that at least one object was stored in S3
    objects = s3_client_mock.list_objects_v2(Bucket="test-bucket")
    assert "Contents" in objects
    assert len(objects["Contents"]) > 0
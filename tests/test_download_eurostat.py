import os
import json
import boto3
import pytest
from moto import mock_aws
from ingestion import download_eurostat


@pytest.fixture(scope="function")
def aws_env(monkeypatch):
    """Set environment variables for S3 bucket and prefix."""
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("S3_PREFIX", "bronze/eurostat/")


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


def test_fetch_single_dataset(requests_mock):
    """Test fetching a single Eurostat dataset."""
    mock_data = {"dataset": "hlth_cd_aro", "value": [1, 2, 3]}
    url = f"{download_eurostat.EUROSTAT_BASE_URL}/hlth_cd_aro?lang=EN&geo=EU27_2020"
    requests_mock.get(url, json=mock_data, status_code=200)

    result = download_eurostat.fetch_eurostat_dataset("hlth_cd_aro")
    assert result == mock_data
    assert "dataset" in result

download_eurostat.S3_BUCKET = "test-bucket"
download_eurostat.S3_PREFIX = "bronze/eurostat/"

def test_lambda_handler_fetches_all(aws_env, s3_client_mock, requests_mock):
    """Test the full Lambda handler: fetch all datasets → save → return keys."""
    # Prepare mock API responses for all datasets
    for dataset_code in download_eurostat.EUROSTAT_DATASETS.keys():
        url = f"{download_eurostat.EUROSTAT_BASE_URL}/{dataset_code}?lang=EN&geo=EU27_2020"
        requests_mock.get(url, json={"dataset": dataset_code, "value": [1]}, status_code=200)

    # Patch boto3 client
    download_eurostat.s3_client = s3_client_mock

    # Fake Lambda context
    class Context:
        aws_request_id = "12345"

    response = download_eurostat.lambda_handler({}, Context())

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert "stored_files" in body
    assert len(body["stored_files"]) == len(download_eurostat.EUROSTAT_DATASETS)

    # Verify that files are in S3
    for dataset_code, key in body["stored_files"].items():
        obj = s3_client_mock.get_object(Bucket="test-bucket", Key=key)
        stored_data = json.loads(obj["Body"].read().decode("utf-8"))
        assert stored_data["dataset"] == dataset_code

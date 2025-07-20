import boto3
from moto import mock_aws
import pytest
import sys

# This must come before any boto3 imports
if "gevent.monkey" in sys.modules:
    pytest.skip("gevent monkey-patching detected", allow_module_level=True)

from moto import mock_aws

@pytest.fixture
def aws_mock():
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")

def test_s3_upload(aws_mock):
    # Test S3 upload logic here
    pass
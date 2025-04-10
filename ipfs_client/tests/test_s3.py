from ipfs_client.utils.s3 import S3Uploader, S3UploadError
from ipfs_client.settings.data_models import IPFSS3Config
import os
from pathlib import Path
from dotenv import load_dotenv
import pytest
import asyncio
from ipfs_cid import cid_sha256_hash

def get_test_s3_config():
    # Load test-specific environment variables
    test_env_path = Path(__file__).parent / '.env.test.s3uploader'
    if not test_env_path.exists():
        raise FileNotFoundError(f'❌ Test environment file not found at {test_env_path}')
    
    load_dotenv(test_env_path)
    
    # get from env variables
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    
    if not all([endpoint_url, bucket_name, access_key, secret_key]):
        raise ValueError('❌ One of the following envs: S3_ENDPOINT_URL, S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_KEY missing')
    
    return IPFSS3Config(
        enabled=True,
        endpoint_url=endpoint_url,  # type: ignore
        bucket_name=bucket_name,  # type: ignore
        access_key=access_key,  # type: ignore
        secret_key=secret_key,  # type: ignore
    )


@pytest.mark.asyncio
async def test_s3_uploader():
    config = get_test_s3_config()
    print('Running test with S3 bucket:', config.bucket_name)
    uploader = S3Uploader(config)
    text_upload = b'Hello, world!'
    
    # Generate IPFS CID v1 for the test data
    expected_cid = cid_sha256_hash(text_upload)
    
    # Upload the data and get the returned CID
    returned_cid = await uploader.upload_file(text_upload)
    
    # Verify that the returned CID matches our expected CID
    assert returned_cid == expected_cid, f"Expected CID {expected_cid}, got {returned_cid}"
    

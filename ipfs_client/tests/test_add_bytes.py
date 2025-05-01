import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from ipfs_client.main import AsyncIPFSClientSingleton
from ipfs_client.settings.data_models import ConnectionLimits
from ipfs_client.settings.data_models import ExternalAPIAuth
from ipfs_client.settings.data_models import IPFSConfig
from ipfs_client.settings.data_models import IPFSS3Config
from ipfs_client.settings.data_models import RemotePinningConfig


@pytest.mark.asyncio
async def test_read_from_cid():
    # Load test-specific environment variables
    test_env_path = Path(__file__).parent / '.env.test.s3uploader'
    if not test_env_path.exists():
        raise FileNotFoundError(
            f'❌ Test environment file not found at {test_env_path}',
        )

    load_dotenv(test_env_path)

    # get from env variables
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')

    ipfs_url = os.getenv('IPFS_URL', 'http://localhost:5001')
    ipfs_auth_api_key = os.getenv('IPFS_AUTH_API_KEY', '')
    ipfs_auth_api_secret = os.getenv('IPFS_AUTH_API_SECRET', '')
    ipfs_client_settings = IPFSConfig(
        url=ipfs_url,
        reader_url=ipfs_url,
        url_auth=ExternalAPIAuth(
            apiKey=ipfs_auth_api_key, apiSecret=ipfs_auth_api_secret,
        ),
        timeout=60,
        connection_limits=ConnectionLimits(
            max_connections=100,
            max_keepalive_connections=50,
            keepalive_expiry=300,
        ),
        remote_pinning=RemotePinningConfig(
            enabled=False,
            service_name='',
            service_endpoint='',
            service_token='',
            background_pinning=False,
        ),
        s3=IPFSS3Config(
            enabled=True,
            endpoint_url=endpoint_url,
            bucket_name=bucket_name,
            access_key=access_key,
            secret_key=secret_key,
        ),
    )
    if all([ipfs_auth_api_key, ipfs_auth_api_secret]):
        ipfs_client_settings.url_auth = ExternalAPIAuth(
            apiKey=ipfs_auth_api_key,
            apiSecret=ipfs_auth_api_secret,
        )
        ipfs_client_settings.reader_url_auth = ExternalAPIAuth(
            apiKey=ipfs_auth_api_key,
            apiSecret=ipfs_auth_api_secret,
        )
    ipfs_client = AsyncIPFSClientSingleton(
        settings=ipfs_client_settings,
    )
    await ipfs_client.init_sessions()
    byte_data = b'test'
    cid = await ipfs_client._ipfs_write_client.add_bytes(byte_data)
    data = await ipfs_client._ipfs_read_client.cat(cid, bytes_mode=False)
    assert data == 'test'


@pytest.mark.asyncio
async def test_add_and_delete_file():
    # Load test-specific environment variables
    test_env_path = Path(__file__).parent / '.env.test.s3uploader'
    if not test_env_path.exists():
        raise FileNotFoundError(
            f'❌ Test environment file not found at {test_env_path}',
        )

    load_dotenv(test_env_path)

    # get from env variables
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')

    ipfs_url = os.getenv('IPFS_URL', 'http://localhost:5001')
    ipfs_auth_api_key = os.getenv('IPFS_AUTH_API_KEY', '')
    ipfs_auth_api_secret = os.getenv('IPFS_AUTH_API_SECRET', '')
    ipfs_client_settings = IPFSConfig(
        url=ipfs_url,
        reader_url=ipfs_url,
        url_auth=ExternalAPIAuth(
            apiKey=ipfs_auth_api_key, apiSecret=ipfs_auth_api_secret,
        ),
        timeout=60,
        connection_limits=ConnectionLimits(
            max_connections=100,
            max_keepalive_connections=50,
            keepalive_expiry=300,
        ),
        remote_pinning=RemotePinningConfig(
            enabled=False,
            service_name='',
            service_endpoint='',
            service_token='',
            background_pinning=False,
        ),
        s3=IPFSS3Config(
            enabled=True,
            endpoint_url=endpoint_url,
            bucket_name=bucket_name,
            access_key=access_key,
            secret_key=secret_key,
        ),
    )
    if all([ipfs_auth_api_key, ipfs_auth_api_secret]):
        ipfs_client_settings.url_auth = ExternalAPIAuth(
            apiKey=ipfs_auth_api_key,
            apiSecret=ipfs_auth_api_secret,
        )
        ipfs_client_settings.reader_url_auth = ExternalAPIAuth(
            apiKey=ipfs_auth_api_key,
            apiSecret=ipfs_auth_api_secret,
        )
    ipfs_client = AsyncIPFSClientSingleton(
        settings=ipfs_client_settings,
    )
    await ipfs_client.init_sessions()

    # Create test file content
    file_content = b'PL: test file content for deletion test'

    # Add file to IPFS
    cid = await ipfs_client._ipfs_write_client.add_bytes(file_content)
    print(f'\n\nAdded file with CID: {cid} - Use this to check manually\n\n')

    # Verify file was added correctly
    retrieved_content = await ipfs_client._ipfs_read_client.cat(cid, bytes_mode=False)
    assert retrieved_content == file_content.decode('utf-8')

    # Verify it's pinned using the API directly
    response = await ipfs_client._ipfs_write_client._client.post(f'/pin/ls?arg={cid}')
    assert response.status_code == 200, 'Failed to check pin status before deletion'
    pin_data_before = json.loads(response.text)
    print(f'Pin status before deletion: {pin_data_before}')
    assert cid in pin_data_before.get(
        'Keys', {},
    ), 'CID was not pinned initially'

    # Delete the file from IPFS (this actually just unpins it from the local node)
    delete_result = await ipfs_client._ipfs_write_client.remove_bytes(cid)
    print(
        f"\n\nRemoved file with CID: {cid} - Check if it's unpinned with 'ipfs pin ls | grep {cid}'\n\n",
    )

    # Check pin status after deletion using the API
    response = await ipfs_client._ipfs_write_client._client.post(f'/pin/ls?arg={cid}')
    print(
        f'Pin status check response: {response.status_code} - {response.text}',
    )

    # If the pin was removed successfully, we should either get:
    # - A 500 error with "not pinned" message
    # - Or a 200 with the CID not in the Keys dictionary
    pin_removed = False
    if response.status_code == 500 and 'not pinned' in response.text.lower():
        pin_removed = True
    elif response.status_code == 200:
        pin_data_after = json.loads(response.text)
        print(f'Pin status after deletion: {pin_data_after}')
        pin_removed = cid not in pin_data_after.get('Keys', {})

    assert pin_removed, 'Pin was not successfully removed'

    # The deletion should have been successful
    assert delete_result is True, 'File unpinning operation failed'

import os

from ipfs_client.main import AsyncIPFSClientSingleton
from ipfs_client.settings.data_models import ConnectionLimits
from ipfs_client.settings.data_models import ExternalAPIAuth
from ipfs_client.settings.data_models import IPFSConfig
from ipfs_client.settings.data_models import IPFSS3Config
from ipfs_client.settings.data_models import RemotePinningConfig
from dotenv import load_dotenv
from pathlib import Path
import pytest

@pytest.mark.asyncio
async def test_remote_pinning():
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

    ipfs_url = os.getenv('IPFS_URL', 'http://localhost:5001')
    ipfs_auth_api_key = os.getenv('IPFS_AUTH_API_KEY', '')
    ipfs_auth_api_secret = os.getenv('IPFS_AUTH_API_SECRET', '')
    ipfs_client_settings = IPFSConfig(
        url=ipfs_url,
        reader_url=ipfs_url,
        url_auth=ExternalAPIAuth(apiKey=ipfs_auth_api_key, apiSecret=ipfs_auth_api_secret),
        timeout=60,
        connection_limits=ConnectionLimits(
            max_connections=100,
            max_keepalive_connections=50,
            keepalive_expiry=300,
        ),
        remote_pinning=RemotePinningConfig(
            enabled=os.getenv('REMOTE_PINNING_ENABLED', False),
            service_name=os.getenv('REMOTE_PINNING_SERVICE_NAME', ''),
            service_endpoint=os.getenv('REMOTE_PINNING_SERVICE_ENDPOINT', ''),
            service_token=os.getenv('REMOTE_PINNING_SERVICE_TOKEN', ''),
            background_pinning=False,
        ),
        s3=IPFSS3Config(
            enabled=True,
            endpoint_url=endpoint_url,
            bucket_name=bucket_name,
            access_key=access_key,
            secret_key=secret_key,
        )
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
    data_to_pin = {'test': 'test'}
    cid = await ipfs_client._ipfs_write_client.add_json(data_to_pin)
    print(cid)
    data = await ipfs_client._ipfs_read_client.get_json(cid)
    assert data == data_to_pin

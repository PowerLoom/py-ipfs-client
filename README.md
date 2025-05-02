# py-ipfs-client

A Python async client library for interacting with IPFS (InterPlanetary File System) nodes.

## Features

- **Fully Asynchronous**: Built on `httpx` and `asyncio` for high-performance I/O operations
- **Content Management**: Add, retrieve, pin, and remove content from IPFS
- **DAG Support**: Work with IPFS DAG (Directed Acyclic Graph) structures
- **Remote Pinning**: Integration with remote pinning services to ensure content persistence
- **S3 Integration**: Store IPFS content in S3-compatible storage for better availability and retrieval
- **Flexible Configuration**: Comprehensive settings for connection limits, timeouts, authentication, and more
- **Separate Read/Write Clients**: Optimized client instances for read and write operations
- **Multiaddr Support**: Connect to IPFS nodes using either URL or multiaddr formats

## Installation

```bash
# Using pip
pip install ifps_client

# Using Poetry
poetry add ifps_client
```

## Quick Start

```python
import asyncio
from ipfs_client.main import AsyncIPFSClientSingleton
from ipfs_client.settings.data_models import (
    IPFSConfig, ConnectionLimits, RemotePinningConfig, IPFSS3Config
)

async def main():
    # Configure the IPFS client
    ipfs_config = IPFSConfig(
        url="http://localhost:5001",              # Primary IPFS API endpoint
        reader_url="http://localhost:5001",       # Read gateway (can be different)
        timeout=60,                               # Request timeout in seconds
        connection_limits=ConnectionLimits(
            max_connections=10,
            max_keepalive_connections=5,
            keepalive_expiry=60,
        ),
        remote_pinning=RemotePinningConfig(
            enabled=False,                        # Enable for remote pinning
        ),
        s3=IPFSS3Config(
            enabled=False,                        # Enable for S3 integration
        ),
    )

    # Create the client singleton
    ipfs_client = AsyncIPFSClientSingleton(settings=ipfs_config)

    # Initialize client sessions (must be called before any operations)
    await ipfs_client.init_sessions()

    # Add JSON data to IPFS
    data = {"example": "Hello IPFS!"}
    cid = await ipfs_client._ipfs_write_client.add_json(data)
    print(f"Added data with CID: {cid}")

    # Retrieve the data from IPFS
    retrieved_data = await ipfs_client._ipfs_read_client.get_json(cid)
    print(f"Retrieved data: {retrieved_data}")

    # Remove data from IPFS (unpins from local node and remote pinning service if configured)
    success = await ipfs_client._ipfs_write_client.remove_json(cid)
    print(f"Data removal successful: {success}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication

The client supports API key authentication for services like Infura:

```python
from ipfs_client.settings.data_models import ExternalAPIAuth

# In your config setup
ipfs_config.url_auth = ExternalAPIAuth(
    apiKey="your_api_key",
    apiSecret="your_api_secret"
)
ipfs_config.reader_url_auth = ExternalAPIAuth(
    apiKey="your_api_key",
    apiSecret="your_api_secret"
)
```

## Remote Pinning

Enable and configure remote pinning services to ensure content persistence:

```python
from ipfs_client.settings.data_models import RemotePinningConfig

ipfs_config.remote_pinning = RemotePinningConfig(
    enabled=True,
    service_name="pinata",                   # Name for your pinning service
    service_endpoint="https://api.pinata.cloud/psa",  # Endpoint URL
    service_token="your_jwt_token",          # Authentication token
    background_pinning=True                  # Pin in background (async)
)
```

## S3 Integration

Store IPFS content in S3-compatible storage:

```python
from ipfs_client.settings.data_models import IPFSS3Config

ipfs_config.s3 = IPFSS3Config(
    enabled=True,
    endpoint_url="https://s3.amazonaws.com",  # S3 endpoint
    bucket_name="my-ipfs-bucket",            # Bucket to store content
    access_key="your_access_key",            # S3 access key
    secret_key="your_secret_key"             # S3 secret key
)
```

## Working with DAG

The client provides methods for interacting with IPFS DAG (Directed Acyclic Graph):

```python
from io import BytesIO
import json

# Prepare DAG data
dag_data = {"links": [], "data": "Hello DAG!"}
dag_bytes = BytesIO(json.dumps(dag_data).encode())

# Add data to DAG
dag_put_result = await ipfs_client._ipfs_write_client.dag.put(dag_bytes)
dag_cid = dag_put_result["Cid"]["/"]

# Retrieve data from DAG
dag_block = await ipfs_client._ipfs_read_client.dag.get(dag_cid)
retrieved_dag_data = dag_block.as_json()
```

## Error Handling

The library provides custom exceptions for different error scenarios:

```python
from ipfs_client.dag import IPFSAsyncClientError
from ipfs_client.exceptions import AddressError
from ipfs_client.utils.s3 import S3UploadError, S3DeleteError

try:
    cid = await ipfs_client._ipfs_write_client.add_json({"test": "data"})
except AddressError:
    print("Invalid IPFS address format")
except IPFSAsyncClientError as e:
    print(f"IPFS operation failed: {str(e)}")
except S3UploadError as e:
    print(f"S3 upload failed: {str(e)}")
except S3DeleteError as e:
    print(f"S3 delete operation failed: {str(e)}")
```

## Connection Management

The client supports configurable connection limits for optimized performance:

```python
from ipfs_client.settings.data_models import ConnectionLimits

# Custom connection limits
conn_limits = ConnectionLimits(
    max_connections=100,             # Maximum total connections in the pool
    max_keepalive_connections=50,    # Maximum idle connections to keep alive
    keepalive_expiry=300             # Time in seconds before an idle connection expires
)

ipfs_config.connection_limits = conn_limits
```

## Multiaddr Support

The client supports both URL and multiaddr formats for IPFS node addresses:

```python
# URL format
ipfs_config.url = "http://localhost:5001"

# Multiaddr format
ipfs_config.url = "/ip4/127.0.0.1/tcp/5001/http"
```

## Running Tests

The library includes a comprehensive test suite that verifies all the functionality works correctly. You can run the tests using Poetry:

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest ipfs_client/tests/test_add_bytes.py

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=ipfs_client
```

### Configuring the Test Environment

Before running tests, you need to set up your test environment configuration. The tests look for environment variables specified in config files:

1. Copy the example environment file to create your test configuration:

```bash
cp ipfs_client/tests/.env.test.s3uploader.example ipfs_client/tests/.env.test.s3uploader
```

2. Edit the `.env.test.s3uploader` file with your test IPFS and S3 configuration:

```bash
# IPFS S3-compatible service test configuration
S3_ENDPOINT_URL=http://your-s3-endpoint
S3_BUCKET_NAME=your-test-bucket
S3_ACCESS_KEY=your-s3-access-key
S3_SECRET_KEY=your-s3-secret-key

# Remote pinning configuration
REMOTE_PINNING_ENABLED=false
REMOTE_PINNING_SERVICE_NAME=pinning-service-name
REMOTE_PINNING_SERVICE_ENDPOINT=pinning-service-endpoint
REMOTE_PINNING_SERVICE_TOKEN=pinning-service-token

# IPFS node configuration (optional)
IPFS_URL=http://localhost:5001
IPFS_AUTH_API_KEY=your-api-key
IPFS_AUTH_API_SECRET=your-api-secret
```

The tests will automatically load this configuration when run, and will fail if the environment file is not found.

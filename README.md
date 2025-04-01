# py-ipfs-client

A Python async client library for interacting with IPFS (InterPlanetary File System) nodes.

## Features

- **Fully Asynchronous**: Built on `httpx` and `asyncio` for high-performance I/O operations
- **Content Management**: Add, retrieve, and pin content to IPFS
- **DAG Support**: Work with IPFS DAG (Directed Acyclic Graph) structures
- **Remote Pinning**: Integration with remote pinning services to ensure content persistence
- **S3 Integration**: Store IPFS content in S3-compatible storage for better availability and retrieval
- **Flexible Configuration**: Comprehensive settings for connection limits, timeouts, authentication, and more
- **Separate Read/Write Clients**: Optimized client instances for read and write operations

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
from ipfs_client.utils.s3 import S3UploadError

try:
    cid = await ipfs_client._ipfs_write_client.add_json({"test": "data"})
except AddressError:
    print("Invalid IPFS address format")
except IPFSAsyncClientError as e:
    print(f"IPFS operation failed: {str(e)}")
except S3UploadError as e:
    print(f"S3 upload failed: {str(e)}")
```

## Multiaddr Support

The client supports both URL and multiaddr formats for IPFS node addresses:

```python
# URL format
ipfs_config.url = "http://localhost:5001"

# Multiaddr format
ipfs_config.url = "/ip4/127.0.0.1/tcp/5001/http"
```

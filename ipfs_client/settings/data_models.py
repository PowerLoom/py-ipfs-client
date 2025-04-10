from typing import Optional

from pydantic import BaseModel


class ConnectionLimits(BaseModel):
    """
    Configuration for HTTP connection pooling limits.
    
    Controls the maximum number of connections, keepalive connections,
    and the expiry time for keepalive connections.
    """
    max_connections: int = 100  # Maximum total connections in the pool
    max_keepalive_connections: int = 50  # Maximum idle connections to keep alive
    keepalive_expiry: int = 300  # Time in seconds before an idle connection expires


class IPFSWriterRateLimit(BaseModel):
    """
    Rate limiting configuration for IPFS write operations.
    
    Prevents overwhelming the IPFS node with too many write requests.
    """
    req_per_sec: int  # Maximum requests per second
    burst: int  # Maximum burst size for request spikes


class ExternalAPIAuth(BaseModel):
    """
    Authentication credentials for external API services.
    
    Typically used as a basic auth tuple of (username, password) or API key authentication.
    """
    # Used as the username in basic auth or as the API key
    apiKey: str
    # Used as the password in basic auth or left empty for API key only auth
    apiSecret: str = ''


class RemotePinningConfig(BaseModel):
    """
    Configuration for remote pinning services.
    
    Remote pinning allows content to be pinned on remote IPFS nodes
    to ensure persistence and availability.
    """
    enabled: bool  # Whether remote pinning is enabled
    service_name: Optional[str] = ""  # Name of the remote pinning service
    service_endpoint: Optional[str] = ""  # API endpoint for the remote pinning service
    service_token: Optional[str] = ""  # Authentication token for the remote pinning service
    background_pinning: Optional[bool] = False  # Whether to pin content asynchronously


class IPFSS3Config(BaseModel):
    """
    Configuration for S3-compatible storage integration with IPFS.
    
    Allows storing IPFS content in S3-compatible storage for better
    persistence and retrieval performance.
    """
    enabled: bool  # Whether S3 integration is enabled
    endpoint_url: str  # S3 API endpoint URL
    bucket_name: str  # S3 bucket name for storing IPFS content
    access_key: str  # S3 access key for authentication
    secret_key: str  # S3 secret key for authentication


class IPFSConfig(BaseModel):
    """
    Main configuration for IPFS client.
    
    Contains all settings needed to interact with IPFS nodes,
    including connection details, authentication, rate limiting,
    and additional features like remote pinning and S3 integration.
    """
    url: str  # Primary IPFS API endpoint URL
    url_auth: Optional[ExternalAPIAuth] = None  # Authentication for primary endpoint
    reader_url: str  # IPFS gateway URL for read operations
    reader_url_auth: Optional[ExternalAPIAuth] = None  # Authentication for reader endpoint
    timeout: int  # Request timeout in seconds
    connection_limits: ConnectionLimits  # HTTP connection pooling configuration
    remote_pinning: RemotePinningConfig  # Remote pinning service configuration
    s3: IPFSS3Config  # S3 integration configuration
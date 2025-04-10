import uuid

import aioboto3
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError

from ipfs_client.default_logger import logger
from ipfs_client.settings.data_models import IPFSS3Config


class S3UploadError(Exception):
    """
    Custom exception for S3 upload errors.
    
    Raised when an upload operation to S3 fails and cannot be recovered
    through the retry mechanism.
    """
    pass


def log_retry(retry_state):
    """
    Log retry attempts for better observability.
    
    Args:
        retry_state: The current state of the retry, containing information
                    about the function being retried and attempt number.
    """
    logger.warning(
        f'Retrying {retry_state.fn.__name__} (attempt {retry_state.attempt_number})',
    )


class S3Uploader:
    """
    Handles uploading files to S3-compatible storage with retry logic.
    
    This class provides functionality to store IPFS content in S3-compatible
    storage for better persistence and retrieval performance.
    """
    
    def __init__(self, config: IPFSS3Config):
        """
        Initialize S3Uploader with configuration.
        
        Args:
            config (IPFSS3Config): Configuration dataclass containing S3 settings
                                  including endpoint URL, bucket name, and credentials.
        """
        self.config = config
        self.session = aioboto3.Session()  # Create aioboto3 session for async operations
        self.client = None  # Client will be lazily initialized when needed

    def _create_client(self):
        """
        Create a new S3 client using the configured settings.
        
        Returns:
            An aioboto3 S3 client context manager
            
        Raises:
            S3UploadError: If client creation fails
        """
        try:
            return self.session.client(
                's3',
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
            )
        except Exception as e:
            logger.error('Failed to create S3 client: {}', str(e))
            raise S3UploadError(f'S3 client creation failed: {str(e)}')

    async def _ensure_client(self):
        """
        Ensure client exists and create if necessary.
        
        This method lazily initializes the S3 client on first use.
        
        Returns:
            An initialized S3 client
        """
        if self.client is None:
            self.client = await self._create_client().__aenter__()
        return self.client

    async def upload_file(
        self,
        data: bytes,
    ) -> str:
        """
        Upload file to S3 with retry logic.
        
        This method handles uploading binary data to the configured S3 bucket.
        It implements exponential backoff retry logic for transient failures.
        
        Args:
            data (bytes): Binary data to upload to S3
            
        Returns:
            str: Content ID (CID) of uploaded file
            
        Raises:
            S3UploadError: If upload fails after all retries
            ValueError: If input validation fails
        """
        try:
            # Get or create S3 client
            client = await self._ensure_client()
            
            # Generate a unique filename to avoid collisions
            random_filename = f'{uuid.uuid4()}.json'
            
            # Upload the object to S3
            response = await client.put_object(
                Bucket=self.config.bucket_name,
                Key=random_filename,
                Body=data,
                Metadata={
                    'cid-version': '1',  # Set CID version metadata
                },
            )

            # Extract the CID from the response metadata
            cid = response['ResponseMetadata']['HTTPHeaders']['x-amz-meta-cid']
            logger.success('Successfully uploaded file {} with CID: {}', random_filename, cid)
            return cid

        except ParamValidationError as e:
            # Handle validation errors (non-retryable)
            logger.error('Parameter validation error: {}', str(e))
            raise ValueError(f'Invalid parameters: {str(e)}')

        except (ClientError, ConnectionError) as e:
            # Handle AWS-specific errors (retryable)
            logger.error('S3 operation failed: {}', str(e))
            self.client = None  # Reset client on error to force recreation
            raise

        except Exception as e:
            # Handle unexpected errors (non-retryable)
            logger.exception('Unexpected error during upload')
            self.client = None  # Reset client on error
            raise S3UploadError(f'Upload failed: {str(e)}')

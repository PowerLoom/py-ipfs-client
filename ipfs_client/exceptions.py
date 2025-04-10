import typing

import multiaddr


class Error(Exception):
    """
    Base class for all exceptions in this module.
    
    This class serves as the parent exception for all custom exceptions
    defined in the IPFS client library, allowing for hierarchical exception
    handling and consistent error patterns.
    """
    __slots__ = ()  # No instance attributes to save memory


# type: ignore[no-any-unimported, misc]
class AddressError(Error, multiaddr.exceptions.Error):
    """
    Raised when the provided daemon location Multiaddr does not match any
    of the supported patterns.
    
    This exception is thrown when attempting to parse or use an IPFS address
    that doesn't conform to the expected multiaddr format, such as
    '/ip4/127.0.0.1/tcp/5001/http'.
    
    Attributes:
        addr (Union[str, bytes]): The invalid multiaddr that caused the error
    """
    __slots__ = ('addr',)  # Only store the address to save memory

    addr: typing.Union[str, bytes]  # Type annotation for the address attribute

    def __init__(self, addr: typing.Union[str, bytes]) -> None:
        """
        Initialize the AddressError with the invalid address.
        
        Args:
            addr (Union[str, bytes]): The invalid multiaddr that caused the error
        """
        self.addr = addr  # Store the invalid address for reference
        Error.__init__(
            self, 'Unsupported Multiaddr pattern: {0!r}'.format(addr),
        )

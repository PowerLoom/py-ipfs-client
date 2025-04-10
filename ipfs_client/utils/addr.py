import socket
import urllib.parse

import multiaddr.exceptions
import validators
from multiaddr.protocols import P_HTTP
from multiaddr.protocols import P_HTTPS
from multiaddr.protocols import P_IP4
from multiaddr.protocols import P_IP6
from multiaddr.protocols import P_TCP

from ipfs_client.exceptions import AddressError


AF_UNIX = getattr(socket, 'AF_UNIX', NotImplemented)


def multiaddr_to_url_data(
        addr, base: str,  # type: ignore[no-any-unimported]
):
    """
    Convert a multiaddr address to URL data suitable for HTTP requests.
    
    This function parses a multiaddr address string and converts it into a base URL
    and a flag indicating whether the host is in numeric form (IP address).
    
    Args:
        addr: A multiaddr address string (e.g., "/ip4/127.0.0.1/tcp/5001/http")
        base: The base path to append to the URL (e.g., "/api/v0")
    
    Returns:
        tuple: A tuple containing:
            - base_url (str): The complete base URL for HTTP requests
            - host_numeric (bool): Flag indicating if the host is a numeric IP address
    
    Raises:
        AddressError: If the multiaddr cannot be parsed or has an invalid format
    """
    try:
        # Parse the multiaddr string into a Multiaddr object
        multi_addr = multiaddr.Multiaddr(addr)
    except multiaddr.exceptions.ParseError as error:
        raise AddressError(addr) from error

    addr_iter = iter(multi_addr.items())

    try:
        # Read host value (should be IP4 or IP6)
        proto, host = next(addr_iter)
        host_numeric = proto.code in (P_IP4, P_IP6)

        # Read port value for IP-based transports (must be TCP)
        proto, port = next(addr_iter)
        if proto.code != P_TCP:
            raise AddressError(addr)

        # Pre-format network location URL part based on host+port
        # Handle IPv6 addresses properly by enclosing them in square brackets
        if ':' in host and not host.startswith('['):
            netloc = '[{0}]:{1}'.format(host, port)
        else:
            netloc = '{0}:{1}'.format(host, port)

        # Read application-level protocol name (HTTP or HTTPS)
        secure = False
        try:
            proto, value = next(addr_iter)
        except StopIteration:
            # No protocol specified, default to HTTP
            pass
        else:
            if proto.code == P_HTTPS:
                secure = True
            elif proto.code != P_HTTP:
                raise AddressError(addr)

        # Ensure there are no additional components in the multiaddr
        was_final = all(False for _ in addr_iter)
        if not was_final:
            raise AddressError(addr)
    except StopIteration:
        # Not enough components in the multiaddr
        raise AddressError(addr) from None

    # Ensure base path ends with a slash
    if not base.endswith('/'):
        base += '/'

    # Construct the complete URL from the parsed components
    base_url = urllib.parse.SplitResult(
        scheme='http' if not secure else 'https',
        netloc=netloc,
        path=base,
        query='',
        fragment='',
    ).geturl()

    return base_url, host_numeric


def is_valid_url(url):
    """
    Check if a string is a valid URL.
    
    Args:
        url (str): The URL string to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    return validators.url(url)

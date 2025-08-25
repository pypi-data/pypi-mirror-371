"""URL utilities for consistent URL handling and validation."""

from dataclasses import dataclass
from typing import Optional, Tuple
from urllib.parse import urlparse


@dataclass
class ParsedURL:
    """Parsed URL with validation information."""

    url: str
    scheme: str
    hostname: Optional[str]
    port: Optional[int]
    is_tcp: bool
    is_http: bool
    is_https: bool

    @property
    def is_valid(self) -> bool:
        """Check if the parsed URL is valid."""
        if self.is_tcp:
            return self.hostname is not None and self.port is not None
        return self.hostname is not None


def parse_and_validate_url(url: str) -> ParsedURL:
    """Parse and validate URL with consistent error handling.

    Args:
        url: URL string to parse

    Returns:
        ParsedURL object with validation information
    """
    parsed = urlparse(url)

    is_tcp = parsed.scheme == "tcp"
    is_http = parsed.scheme == "http"
    is_https = parsed.scheme == "https"

    return ParsedURL(
        url=url,
        scheme=parsed.scheme,
        hostname=parsed.hostname,
        port=parsed.port,
        is_tcp=is_tcp,
        is_http=is_http,
        is_https=is_https,
    )


def preprocess_url(url: str) -> str:
    """Preprocess URL by adding http:// if no scheme is provided.

    Args:
        url: Raw URL string

    Returns:
        URL with scheme
    """
    parsed = urlparse(url)
    if not parsed.scheme:
        return f"http://{url}"
    return url


def extract_hostname_port(url: str) -> Tuple[Optional[str], Optional[int]]:
    """Extract hostname and port from URL.

    Args:
        url: URL string to parse

    Returns:
        Tuple of (hostname, port)
    """
    parsed = urlparse(url)
    return parsed.hostname, parsed.port


def validate_tcp_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate TCP URL format.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    parsed_url = parse_and_validate_url(url)

    if not parsed_url.is_tcp:
        return True, None  # Not a TCP URL, so it's fine

    if not parsed_url.hostname:
        return False, "TCP URLs must include a hostname"

    if not parsed_url.port:
        return False, "TCP URLs must include a port (e.g., tcp://example.com:80)"

    return True, None


def replace_hostname_with_ip(url: str, hostname: str, ip: str) -> str:
    """Replace hostname with IP address in URL for DNS resolution caching.

    Args:
        url: Original URL
        hostname: Hostname to replace
        ip: IP address to use instead

    Returns:
        URL with hostname replaced by IP
    """
    return url.replace(hostname, ip, 1)

import asyncio
import socket
import time
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional
from urllib.parse import urlparse

import httpx

from .config import Config


@dataclass
class ProbePhases:
    """Detailed timing breakdown for different phases of a network probe.

    This class captures timing information for each phase of a network request,
    from DNS resolution through connection establishment, TLS handshake,
    request transmission, and response reception. Used for detailed latency
    analysis and performance troubleshooting.

    All timing values are in milliseconds. None indicates the phase was
    not applicable or not measured for this particular probe.
    """

    dns: Optional[float]  # DNS resolution time in ms
    connect: Optional[float]  # TCP connection establishment time in ms
    tls: Optional[float]  # TLS handshake time in ms (HTTPS only)
    request_write: Optional[float]  # Time to send request data in ms
    ttfb: Optional[float]  # Time to first byte of response in ms
    body_read: Optional[float]  # Time to read response body in ms
    total: float  # Total end-to-end latency in ms


@dataclass
class ProbeResult:
    """Result of a single network probe containing timing and response data.

    This class encapsulates all information gathered from a single probe operation,
    including timing measurements, response metadata, error information, and
    host details. Used throughout sping for data processing, display, and export.

    The anomaly flag is set by the metrics system when this result is identified
    as an outlier based on statistical analysis of recent measurements.
    """

    ts: float  # Unix timestamp when probe was initiated
    seq: int  # Sequence number for this probe (1-based)
    latency_ms: float  # Total latency in milliseconds
    status_code: Optional[int]  # HTTP status code (None for TCP or errors)
    error: Optional[str]  # Error message if probe failed
    bytes_read: int  # Number of response bytes received
    content_type: Optional[str]  # Response content type or "tcp/connection"
    host_address: Optional[str]  # Resolved host address (hostname + IP)
    anomaly: bool = False  # True if flagged as statistical outlier
    phases: Optional[ProbePhases] = None  # Detailed timing breakdown

    def to_dict(self):
        """Convert ProbeResult to dictionary for JSON serialization.

        Creates a dictionary representation suitable for JSON export,
        including nested phase timing data when available.

        Returns:
            dict: Complete probe result data ready for serialization
        """
        result = {
            "ts": self.ts,
            "seq": self.seq,
            "latency_ms": self.latency_ms,
            "status": self.status_code,
            "error": self.error,
            "bytes": self.bytes_read,
            "content_type": self.content_type,
            "host_address": self.host_address,
            "anomaly": self.anomaly,
        }
        if self.phases:
            result["phases"] = {
                "dns": self.phases.dns,
                "connect": self.phases.connect,
                "tls": self.phases.tls,
                "request_write": self.phases.request_write,
                "ttfb": self.phases.ttfb,
                "body_read": self.phases.body_read,
                "total": self.phases.total,
            }
        return result


async def resolve_hostname_with_timing(
    hostname: str, cfg: Config
) -> tuple[Optional[str], Optional[float], Optional[str]]:
    """Resolve hostname to IP address with precise timing measurement.

    Performs DNS resolution for the given hostname while measuring the time
    taken and respecting IPv4/IPv6 preferences from configuration. Handles
    various DNS error conditions and provides detailed error reporting.

    Args:
        hostname: Domain name to resolve (e.g., "example.com")
        cfg: Configuration object containing IP version preferences

    Returns:
        tuple: (resolved_ip, dns_time_ms, error_message)
            - resolved_ip: First resolved IP address (None on failure)
            - dns_time_ms: DNS resolution time in milliseconds (None on failure)
            - error_message: Human-readable error description (None on success)

    Error Types:
        - "NoAddressFound": DNS server returned no results
        - "DNSError:reason": DNS resolution failed with specific reason
        - "DNSError:ClassName": Unexpected exception during resolution
    """
    if not hostname:
        return None, None, None

    start_dns = time.monotonic_ns()
    try:
        # Determine address family
        family = socket.AF_UNSPEC  # Default: allow both IPv4 and IPv6
        if cfg.ipv4_only:
            family = socket.AF_INET
        elif cfg.ipv6_only:
            family = socket.AF_INET6

        # Resolve hostname
        loop = asyncio.get_event_loop()
        try:
            result = await loop.getaddrinfo(
                hostname, None, family=family, type=socket.SOCK_STREAM
            )
            if result:
                resolved_ip = result[0][4][0]  # First result's IP address
                end_dns = time.monotonic_ns()
                dns_time_ms = (end_dns - start_dns) / 1_000_000.0
                return resolved_ip, dns_time_ms, None
            else:
                return None, None, "NoAddressFound"
        except socket.gaierror as e:
            return None, None, f"DNSError:{e.strerror}"
    except Exception as e:
        return None, None, f"DNSError:{e.__class__.__name__}"


async def probe_tcp_once(
    cfg: Config, seq: int, hostname: str, port: int, resolved_ip: Optional[str] = None
) -> ProbeResult:
    """Perform a single TCP connection probe with detailed timing measurement.

    Establishes a TCP connection to the specified host and port, measuring
    DNS resolution time (if needed) and connection establishment time.
    This function is used for TCP-only monitoring (tcp:// URLs).

    The function handles the complete TCP probe lifecycle:
    1. DNS resolution (if IP not pre-resolved)
    2. TCP socket connection with timeout
    3. Immediate disconnection (no data transfer)
    4. Timing measurement and error handling

    Args:
        cfg: Configuration object containing timeout and IP preferences
        seq: Sequence number for this probe (used in result tracking)
        hostname: Target hostname to connect to
        port: Target TCP port number
        resolved_ip: Pre-resolved IP address (skips DNS if provided)

    Returns:
        ProbeResult: Complete probe result with timing and status information
            - status_code: 0 for successful connection, None for errors
            - content_type: "tcp/connection" for successful probes
            - phases: Detailed breakdown including DNS and connect times
            - error: Descriptive error message if connection failed

    Error Types:
        - DNS errors: Propagated from resolve_hostname_with_timing()
        - "ConnectionTimeout": TCP connection timed out
        - "ConnectionRefused": Target host refused connection
        - "OSError:reason": Low-level socket error
        - "TCPError:ClassName": Unexpected connection error
        - "UnexpectedError:ClassName": Unexpected exception
    """
    overall_start = time.monotonic_ns()
    error = None
    host_address = None

    # Initialize phase timings
    dns_time: Optional[float] = None
    connect_time: Optional[float] = None

    try:
        # DNS resolution timing (if not already resolved)
        target_ip = resolved_ip
        if not resolved_ip:
            target_ip, dns_time, dns_error = await resolve_hostname_with_timing(
                hostname, cfg
            )
            if dns_error:
                error = dns_error
                end_overall = time.monotonic_ns()
                latency_ms = (end_overall - overall_start) / 1_000_000.0
                phases = ProbePhases(
                    dns=dns_time,
                    connect=None,
                    tls=None,
                    request_write=None,
                    ttfb=None,
                    body_read=None,
                    total=latency_ms,
                )
                return ProbeResult(
                    ts=time.time(),
                    seq=seq,
                    latency_ms=latency_ms,
                    status_code=None,
                    error=error,
                    bytes_read=0,
                    content_type=None,
                    host_address=None,
                    phases=phases,
                )

        if not target_ip:
            error = "NoIPResolved"
            end_overall = time.monotonic_ns()
            latency_ms = (end_overall - overall_start) / 1_000_000.0
            phases = ProbePhases(
                dns=dns_time,
                connect=None,
                tls=None,
                request_write=None,
                ttfb=None,
                body_read=None,
                total=latency_ms,
            )
            return ProbeResult(
                ts=time.time(),
                seq=seq,
                latency_ms=latency_ms,
                status_code=None,
                error=error,
                bytes_read=0,
                content_type=None,
                host_address=None,
                phases=phases,
            )

        # Set host address for display
        host_address = (
            f"{hostname} ({target_ip})" if hostname != target_ip else target_ip
        )

        # TCP connection timing
        connect_start = time.monotonic_ns()
        try:
            # Create connection with timeout
            future = asyncio.open_connection(target_ip, port)
            reader, writer = await asyncio.wait_for(future, timeout=cfg.timeout)
            connect_end = time.monotonic_ns()
            connect_time = (connect_end - connect_start) / 1_000_000.0

            # Close connection immediately
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass  # Ignore close errors

        except asyncio.TimeoutError:
            error = "ConnectionTimeout"
        except ConnectionRefusedError:
            error = "ConnectionRefused"
        except OSError as e:
            error = f"OSError:{e.strerror if hasattr(e, 'strerror') else str(e)}"
        except Exception as e:
            error = f"TCPError:{e.__class__.__name__}"

    except Exception as e:
        error = f"UnexpectedError:{e.__class__.__name__}"

    end_overall = time.monotonic_ns()
    total_latency_ms = (end_overall - overall_start) / 1_000_000.0

    phases = ProbePhases(
        dns=dns_time,
        connect=connect_time,
        tls=None,  # No TLS for plain TCP
        request_write=None,
        ttfb=None,
        body_read=None,
        total=total_latency_ms,
    )

    # For TCP, we use a pseudo status code: 0 for success, None for error
    status_code = 0 if not error else None

    return ProbeResult(
        ts=time.time(),
        seq=seq,
        latency_ms=total_latency_ms,
        status_code=status_code,
        error=error,
        bytes_read=0,
        content_type="tcp/connection" if not error else None,
        host_address=host_address,
        phases=phases,
    )


async def probe_once(
    client: httpx.AsyncClient,
    cfg: Config,
    seq: int,
    url: str,
    resolved_ip: Optional[str] = None,
) -> ProbeResult:
    """Perform a single HTTP/HTTPS probe with comprehensive timing measurement.

    Executes an HTTP request using the provided client, measuring overall latency
    and attempting to capture detailed phase timing where possible. Handles
    various HTTP scenarios including redirects, authentication, and different
    response types.

    The function performs the complete HTTP probe lifecycle:
    1. DNS resolution (if IP not pre-resolved)
    2. HTTP request execution with configured method and headers
    3. Response processing (headers + optional body reading)
    4. Timing measurement and metadata extraction

    Args:
        client: Configured httpx.AsyncClient for making requests
        cfg: Configuration object with request parameters and preferences
        seq: Sequence number for this probe (used in result tracking)
        url: Target URL to probe (may have hostname replaced with IP)
        resolved_ip: Pre-resolved IP address (None if DNS should be measured)

    Returns:
        ProbeResult: Complete probe result with HTTP response data
            - status_code: HTTP status code from response
            - content_type: Response Content-Type header value
            - bytes_read: Total bytes received (headers + body if requested)
            - host_address: "hostname (ip)" format for display
            - phases: Timing breakdown (currently limited by httpx capabilities)
            - error: Descriptive error message if request failed

    Phase Timing Limitations:
        Current implementation only captures TTFB and body read times accurately.
        Connection, TLS, and request write times require custom transport
        implementation and are marked as TODO items.

    Error Types:
        - DNS errors: Propagated from resolve_hostname_with_timing()
        - HTTP errors: Network timeouts, connection errors, etc.
        - Response errors: Invalid responses, protocol errors
    """
    overall_start = time.monotonic_ns()
    error = None
    status_code: Optional[int] = None
    bytes_read = 0
    content_type: Optional[str] = None
    host_address: Optional[str] = None

    # Initialize phase timings
    dns_time: Optional[float] = None
    connect_time: Optional[float] = None
    tls_time: Optional[float] = None
    request_write_time: Optional[float] = None
    ttfb_time: Optional[float] = None
    body_read_time: Optional[float] = None

    try:
        # Parse URL to get hostname
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        # DNS resolution timing (if not already resolved)
        actual_ip = resolved_ip
        if not resolved_ip and hostname:
            actual_ip, dns_time, dns_error = await resolve_hostname_with_timing(
                hostname, cfg
            )
            if dns_error:
                error = dns_error
                end_overall = time.monotonic_ns()
                latency_ms = (end_overall - overall_start) / 1_000_000.0
                phases = ProbePhases(
                    dns=dns_time,
                    connect=None,
                    tls=None,
                    request_write=None,
                    ttfb=None,
                    body_read=None,
                    total=latency_ms,
                )
                return ProbeResult(
                    ts=time.time(),
                    seq=seq,
                    latency_ms=latency_ms,
                    status_code=status_code,
                    error=error,
                    bytes_read=bytes_read,
                    content_type=content_type,
                    host_address=host_address,
                    phases=phases,
                )

        # Perform HTTP request
        request_start = time.monotonic_ns()
        r = await client.request(cfg.method, url)
        response_received = time.monotonic_ns()

        status_code = r.status_code
        content_type = r.headers.get("content-type")

        # Calculate TTFB (Time to First Byte) - time from request start to response headers
        ttfb_time = (response_received - request_start) / 1_000_000.0

        # Format host address
        if hostname and actual_ip and hostname != actual_ip:
            host_address = f"{hostname} ({actual_ip})"
        elif hostname:
            host_address = hostname
        elif actual_ip:
            host_address = actual_ip

        # Handle body reading if needed
        body_start = (
            time.monotonic_ns() if (cfg.include_body or cfg.method != "HEAD") else None
        )
        if cfg.include_body or cfg.method != "HEAD":
            content = r.content  # bytes
            bytes_read = len(content)
            body_end = time.monotonic_ns()
            body_read_time = (
                (body_end - body_start) / 1_000_000.0 if body_start else None
            )

    except Exception as e:
        # Classify error types
        error_name = e.__class__.__name__
        if "timeout" in str(e).lower() or error_name in [
            "ReadTimeout",
            "ConnectTimeout",
            "TimeoutException",
        ]:
            error = "Timeout"
        elif error_name in ["ConnectError", "ConnectionRefused"]:
            error = "ConnectRefused"
        elif (
            "ssl" in str(e).lower()
            or "tls" in str(e).lower()
            or error_name in ["SSLError"]
        ):
            error = "TLSError"
        else:
            error = error_name

    end_overall = time.monotonic_ns()
    total_latency_ms = (end_overall - overall_start) / 1_000_000.0

    # Create phases object
    phases = ProbePhases(
        dns=dns_time,
        connect=connect_time,  # TODO: Need custom transport to measure this accurately
        tls=tls_time,  # TODO: Need custom transport to measure this accurately
        request_write=request_write_time,  # TODO: Need custom transport to measure this accurately
        ttfb=ttfb_time,
        body_read=body_read_time,
        total=total_latency_ms,
    )

    return ProbeResult(
        ts=time.time(),
        seq=seq,
        latency_ms=total_latency_ms,
        status_code=status_code,
        error=error,
        bytes_read=bytes_read,
        content_type=content_type,
        host_address=host_address,
        phases=phases,
    )


async def probe_stream(cfg: Config) -> AsyncIterator[ProbeResult]:
    """Generate a continuous stream of probe results based on configuration.

    This is the main entry point for probe execution, handling both TCP and HTTP
    monitoring modes. Creates appropriate probe infrastructure, manages timing
    intervals, and yields results continuously until stopped or count limit reached.

    The function automatically detects probe type from URL scheme:
    - tcp:// URLs: Direct TCP connection probing via probe_tcp_once()
    - http/https:// URLs: HTTP request probing via probe_once()

    Key Features:
    - Precise interval timing with drift correction
    - Optional DNS resolution caching (resolve_once mode)
    - Configurable probe count limits
    - Graceful cancellation handling
    - Automatic client configuration for HTTP probes

    TCP Mode Behavior:
    - Validates hostname and port requirements
    - Performs direct socket connections
    - Measures connection establishment time
    - No data transfer, immediate disconnect

    HTTP Mode Behavior:
    - Creates httpx.AsyncClient with full configuration
    - Supports authentication, custom headers, TLS settings
    - Measures full request/response cycle
    - Optional body reading for complete transfer timing

    Args:
        cfg: Complete configuration object containing:
            - url: Target URL (tcp://, http://, or https://)
            - interval: Time between probes in seconds
            - count: Maximum probes (None for unlimited)
            - timeout: Per-probe timeout in seconds
            - resolve_once: Cache DNS resolution flag
            - Plus all HTTP-specific settings

    Yields:
        ProbeResult: Individual probe results as they complete
            - Immediate yield for each probe (no buffering)
            - Results include timing, status, and error information
            - Sequence numbers start at 1 and increment

    Raises:
        asyncio.CancelledError: When stream is cancelled (handled gracefully)

    Timing Behavior:
        Uses drift correction to maintain precise intervals regardless of
        probe execution time. Each probe is scheduled at exact intervals
        from the start time, not relative to the previous probe completion.

    Error Handling:
        Individual probe errors are captured in ProbeResult.error field
        and do not stop the stream. Only fatal configuration errors or
        cancellation will terminate the stream.
    """
    # Check if this is a TCP probe
    parsed_url = urlparse(cfg.url)
    is_tcp = parsed_url.scheme == "tcp"

    if is_tcp:
        # Handle TCP probing
        hostname = parsed_url.hostname
        port = parsed_url.port

        if not hostname:
            # Return error result for invalid TCP URL
            error_result = ProbeResult(
                ts=time.time(),
                seq=1,
                latency_ms=0.0,
                status_code=None,
                error="InvalidTCPURL:NoHostname",
                bytes_read=0,
                content_type=None,
                host_address=None,
            )
            yield error_result
            return

        if not port:
            # Return error result for missing port
            error_result = ProbeResult(
                ts=time.time(),
                seq=1,
                latency_ms=0.0,
                status_code=None,
                error="InvalidTCPURL:NoPort",
                bytes_read=0,
                content_type=None,
                host_address=None,
            )
            yield error_result
            return

        # Handle DNS resolution once for TCP
        resolved_ip = None
        if cfg.resolve_once:
            try:
                resolved_ip, _, dns_error = await resolve_hostname_with_timing(
                    hostname, cfg
                )
                if dns_error:
                    resolved_ip = None
            except Exception:
                resolved_ip = None

        # TCP probing loop
        seq = 0
        start_time = time.monotonic()
        while True:
            seq += 1
            scheduled_next = start_time + seq * cfg.interval
            res = await probe_tcp_once(cfg, seq, hostname, port, resolved_ip)
            yield res
            if cfg.count and seq >= cfg.count:
                break
            # drift correction
            now = time.monotonic()
            sleep_for = scheduled_next - now
            if sleep_for > 0:
                try:
                    await asyncio.sleep(sleep_for)
                except asyncio.CancelledError:
                    break
        return

    # Original HTTP probing logic
    timeout = httpx.Timeout(cfg.timeout)

    # Build client configuration
    client_kwargs: dict[str, Any] = {
        "timeout": timeout,
    }

    # Handle keep-alive setting
    if not cfg.keepalive:
        client_kwargs["limits"] = httpx.Limits(max_keepalive_connections=0)

    # Handle TLS verification
    if cfg.insecure:
        client_kwargs["verify"] = False

    # Handle authentication
    auth = None
    if cfg.auth:
        if cfg.auth.startswith("bearer:"):
            # Bearer token auth
            token = cfg.auth[7:]  # Remove 'bearer:' prefix
            client_kwargs["headers"] = {"Authorization": f"Bearer {token}"}
        elif ":" in cfg.auth:
            # Basic auth
            user, password = cfg.auth.split(":", 1)
            auth = (user, password)

    if auth:
        client_kwargs["auth"] = auth

    # Set custom user agent
    headers: dict[str, str] = client_kwargs.get("headers", {})
    if cfg.user_agent:
        headers["User-Agent"] = cfg.user_agent
    if headers:
        client_kwargs["headers"] = headers

    # Handle DNS resolution once
    resolved_ip = None
    if cfg.resolve_once:
        try:
            parsed_url = urlparse(cfg.url)
            hostname = parsed_url.hostname
            if hostname:
                resolved_ip, _, dns_error = await resolve_hostname_with_timing(
                    hostname, cfg
                )
                if dns_error:
                    # If DNS resolution fails, we'll let individual probes handle it
                    resolved_ip = None
                if resolved_ip:
                    # Replace hostname with IP in URL for subsequent requests
                    modified_url = cfg.url.replace(hostname, resolved_ip, 1)
                else:
                    modified_url = cfg.url
            else:
                modified_url = cfg.url
        except Exception:
            modified_url = cfg.url
    else:
        modified_url = cfg.url

    async with httpx.AsyncClient(**client_kwargs) as client:
        seq = 0
        start_time = time.monotonic()
        while True:
            seq += 1
            scheduled_next = start_time + seq * cfg.interval
            res = await probe_once(client, cfg, seq, modified_url, resolved_ip)
            yield res
            if cfg.count and seq >= cfg.count:
                break
            # drift correction
            now = time.monotonic()
            sleep_for = scheduled_next - now
            if sleep_for > 0:
                try:
                    await asyncio.sleep(sleep_for)
                except asyncio.CancelledError:
                    break

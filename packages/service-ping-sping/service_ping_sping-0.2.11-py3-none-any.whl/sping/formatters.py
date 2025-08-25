"""Response formatting utilities for consistent output across modes."""

from typing import List

from .probe import ProbeResult


def format_status_code(result: ProbeResult) -> str:
    """Format status code consistently for TCP vs HTTP.

    Args:
        result: ProbeResult containing status and protocol information

    Returns:
        Formatted status string
    """
    if result.content_type == "tcp/connection":
        # TCP connection result
        if result.status_code == 0:
            return "connected"
        else:
            return "failed"
    else:
        # HTTP result
        return str(result.status_code) if result.status_code else "error"


def format_response_info(result: ProbeResult) -> List[str]:
    """Format response information consistently across output modes.

    Args:
        result: ProbeResult containing response data

    Returns:
        List of formatted response info parts
    """
    response_parts = []

    if result.error:
        return [f"error: {result.error}"]

    # Status - handle TCP vs HTTP differently
    if result.content_type == "tcp/connection":
        # TCP connection result
        if result.status_code == 0:
            response_parts.append("connected")
        else:
            response_parts.append("failed")
    else:
        # HTTP status code
        if result.status_code:
            response_parts.append(str(result.status_code))

    # Bytes
    if result.bytes_read > 0:
        if result.bytes_read >= 1024:
            response_parts.append(f"{result.bytes_read/1024:.1f}KB")
        else:
            response_parts.append(f"{result.bytes_read}B")

    # Content type
    if result.content_type:
        response_parts.append(format_content_type(result.content_type))

    return response_parts


def format_content_type(content_type: str) -> str:
    """Format content type in a shortened, user-friendly way.

    Args:
        content_type: Raw content-type header value

    Returns:
        Shortened content type string
    """
    # Shorten common content types
    if content_type == "tcp/connection":
        return "tcp"
    elif "text/html" in content_type:
        return "html"
    elif "application/json" in content_type:
        return "json"
    elif "text/plain" in content_type:
        return "text"
    elif "image/" in content_type:
        return "image"
    else:
        # Take first part before semicolon and show last segment
        ct_clean = content_type.split(";")[0]
        if "/" in ct_clean:
            return ct_clean.split("/")[-1]
        else:
            return ct_clean


def format_probe_data_for_json(result: ProbeResult) -> dict:
    """Format probe result for JSON output consistently.

    Args:
        result: ProbeResult to format

    Returns:
        Dictionary suitable for JSON serialization
    """
    probe_data = {
        "seq": result.seq,
        "timestamp": result.ts,
        "latency_ms": result.latency_ms,
        "status_code": result.status_code,
        "error": result.error,
        "bytes_read": result.bytes_read,
        "content_type": result.content_type,
        "host_address": result.host_address,
        "anomaly": getattr(result, "anomaly", False),
    }

    # Add phase information if available
    if result.phases:
        probe_data["phases"] = {
            "dns_ms": result.phases.dns,
            "connect_ms": result.phases.connect,
            "tls_ms": result.phases.tls,
            "request_write_ms": result.phases.request_write,
            "ttfb_ms": result.phases.ttfb,
            "body_read_ms": result.phases.body_read,
            "total_ms": result.phases.total,
        }

    return probe_data


def format_plain_output_line(result: ProbeResult, config=None) -> str:
    """Format a single probe result for plain text output.

    Args:
        result: ProbeResult to format
        config: Optional Config object for threshold checking

    Returns:
        Formatted plain text line
    """
    if result.error:
        error_marker = " [OUTLIER]" if getattr(result, "anomaly", False) else ""
        return f"[{result.seq}] {result.ts}: error: {result.error}{error_marker}"

    response_info = format_response_info(result)
    response_str = f" ({', '.join(response_info)})" if response_info else ""
    host_str = f" from {result.host_address}" if result.host_address else ""
    anomaly_marker = " [OUTLIER]" if getattr(result, "anomaly", False) else ""

    threshold_marker = ""
    if config:
        if config.crit_threshold and result.latency_ms > config.crit_threshold:
            threshold_marker = " [CRITICAL]"
        elif config.warn_threshold and result.latency_ms > config.warn_threshold:
            threshold_marker = " [WARNING]"

    # Format status for TCP vs HTTP
    status_str = format_status_code(result)

    return (
        f"[{result.seq}] {result.ts}: {result.latency_ms:.3f}ms {status_str}"
        f"{response_str}{host_str}{anomaly_marker}{threshold_marker}"
    )

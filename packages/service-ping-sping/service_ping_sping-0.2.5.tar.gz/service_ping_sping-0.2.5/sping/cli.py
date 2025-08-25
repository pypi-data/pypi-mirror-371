"""CLI interface for sping."""

import asyncio
import json
import time
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .config import Config
from .formatters import (
    format_content_type,
    format_plain_output_line,
    format_probe_data_for_json,
)
from .metrics import Metrics
from .probe import probe_stream
from .ui.chart import BarChart
from .ui.colors import ColorPalette, get_latency_color


async def run(cfg: Config):
    """Main application runner that orchestrates the sping monitoring session.

    This is the core function that handles the entire lifecycle of a sping session,
    including probe execution, result processing, UI rendering, and cleanup.
    Supports three output modes: interactive (default), JSON, and plain text.

    Args:
        cfg: Configuration object containing all user-specified options

    Returns:
        int: Exit code (0=success, 1=warning threshold exceeded, 2=critical threshold exceeded)

    Raises:
        KeyboardInterrupt: Handled gracefully during interactive mode
    """
    console = Console()
    metrics = Metrics()

    # Track threshold violations for exit codes
    warn_violations = 0
    crit_violations = 0

    # Setup file export if requested
    export_file_handle = None
    if cfg.export_file:
        try:
            export_file_handle = open(cfg.export_file, "a")
        except Exception as e:
            console.print(
                f"[red]Warning: Could not open export file {cfg.export_file}: {e}[/]"
            )

    async def handle_result(r):
        """Process each probe result for metrics, thresholds, and output.

        This nested function handles the processing of individual probe results
        including metrics updates, threshold checking, file export, and output
        formatting based on the current mode.

        Args:
            r: ProbeResult object containing latency, error, and response data

        Side Effects:
            - Updates global metrics object
            - Increments threshold violation counters
            - Writes to export file if configured
            - Prints output in JSON/plain modes
        """
        nonlocal warn_violations, crit_violations

        metrics.update(r)

        # Check thresholds for successful probes
        if r.error is None:
            if cfg.crit_threshold and r.latency_ms > cfg.crit_threshold:
                crit_violations += 1
            elif cfg.warn_threshold and r.latency_ms > cfg.warn_threshold:
                warn_violations += 1

        # Export to file if configured
        if export_file_handle:
            try:
                export_file_handle.write(json.dumps(r.to_dict()) + "\n")
                export_file_handle.flush()
            except Exception:
                pass  # Fail silently for export errors

        if cfg.mode == "json":
            probe_data = format_probe_data_for_json(r)
            print(json.dumps(probe_data))
        elif cfg.mode == "plain":
            print(format_plain_output_line(r, cfg))

    results_aiter = probe_stream(cfg)

    try:
        if cfg.mode != "interactive":
            async for r in results_aiter:
                await handle_result(r)
            # summary
            s = metrics.summary()
            summary_lines = [
                f"--- {cfg.url} sping summary ---",
                f"{s['count']} probes, {s['ok']} ok, {s['errors']} errors",
            ]

            if s.get("anomalies", 0) > 0:
                summary_lines.append(f"Outliers detected: {s['anomalies']}")

            latency_line = f"Latency (ms): min {s['min']:.3f} mean {s['mean']:.3f} max {s['max']:.3f}"
            if cfg.show_percentiles and s.get("p50") is not None:
                latency_line += f" p50 {s['p50']:.3f} p90 {s['p90']:.3f} p95 {s['p95']:.3f} p99 {s['p99']:.3f}"
            summary_lines.append(latency_line)

            if s["count"] > 1:
                summary_lines.append(f"Standard deviation: {s.get('stdev', 0):.3f}ms")

            if warn_violations > 0 or crit_violations > 0:
                summary_lines.append(
                    f"Threshold violations: {warn_violations} warnings, {crit_violations} critical"
                )

            console.print("\n".join(summary_lines))

            # Determine exit code
            if crit_violations > 0:
                return 2  # Critical threshold exceeded
            elif warn_violations > 0:
                return 1  # Warning threshold exceeded
            return 0

        # interactive mode continues as before but with outlier detection...
        def compute_top_height() -> int:
            """Calculate optimal height for the chart panel based on terminal size.

            Dynamically computes the chart height to use approximately 40% of the
            available vertical space, with reasonable bounds to ensure usability
            on both small and large terminals.

            Returns:
                int: Chart height in rows, bounded between 5 and 15
            """
            # Reserve ~40% of vertical real estate within bounds
            term_h = console.size.height
            # subtract panel borders & summary lines (approx 6)
            usable = max(5, term_h - 6)
            target = int(usable * 0.4)
            return max(5, min(target, 15))

        def render_panel():
            """Render the complete interactive UI panel with chart and log table.

            Creates the main UI layout consisting of:
            1. Top panel: Real-time latency chart with gradient coloring
            2. Bottom panel: Recent events log with host, response, and latency info

            Handles dynamic sizing, IP change detection, color coding, and
            formatting of all displayed data elements.

            Returns:
                Rich Table.grid: Complete UI layout ready for Live display
            """
            # Determine width
            width = console.size.width - 4
            if width < 20:
                width = 20
            # Data
            latencies = metrics.last_latencies(width)
            top_height = compute_top_height()

            # Don't start drawing the bar graph until we have at least one poll result
            # This prevents y-scale rendering issues and incorrect bar positioning at startup
            if not latencies:
                # Show empty chart while waiting for first result
                chart = BarChart(
                    [], width - 2, top_height, cfg.color_palette
                )  # -2 for panel padding
            else:
                chart = BarChart(
                    latencies, width - 2, top_height, cfg.color_palette
                )  # -2 for panel padding

            # Calculate time span for the chart
            chart_title = f"sping {cfg.url}"
            if len(latencies) > 1:
                # Get the time span of the data shown in the chart
                time_span_seconds = len(latencies)  # Each bar represents 1 second
                if time_span_seconds >= 60:
                    time_span_minutes = time_span_seconds / 60
                    chart_title += f" (last {time_span_minutes:.1f}m)"
                else:
                    chart_title += f" (last {time_span_seconds}s)"

            stats = metrics.summary()
            stat_text = (
                f"count {stats['count']} [deep_sky_blue1]ok {stats['ok']}[/] [orange_red1]err {stats['errors']}[/] "
                f"min {stats['min']:.1f} [medium_purple1]mean {stats['mean']:.1f}[/] max {stats['max']:.1f}"
                if stats["count"] > 0
                else "(waiting for samples)"
            )
            if stats.get("anomalies", 0) > 0:
                stat_text += f" [red]outliers {stats['anomalies']}[/]"

            top_content = chart
            # Log panel - fixed height with padding for empty rows
            log_panel = Table(box=None, expand=True, show_header=True)
            log_panel.add_column("Seq", justify="left", width=4)
            log_panel.add_column("Time", width=8)
            log_panel.add_column("Host", width=25)
            log_panel.add_column("Response")
            log_panel.add_column("Latency", justify="right", width=8)

            # Get events and pad to always show 10 rows
            events = metrics.tail_events(10)

            # Get full event history for accurate IP change detection
            all_events = list(metrics.events)

            # Calculate min/max latency for consistent coloring (excluding errors)
            valid_latencies = [e.latency_ms for e in events if e.error is None]
            if valid_latencies:
                min_latency = min(valid_latencies)
                max_latency = max(valid_latencies)
            else:
                min_latency = max_latency = 0.0

            # Use centralized latency color function

            for i in range(10):
                if i < len(events):
                    row = events[i]

                    # Format time (HH:MM:SS)
                    import datetime

                    time_str = f"[grey50]{datetime.datetime.fromtimestamp(row.ts).strftime('%H:%M:%S')}[/]"

                    # Host address - highlight IP in pink if it changed from previous
                    host_str = ""
                    if row.host_address:
                        # Find this event in the full history to get accurate previous event
                        prev_ip = None
                        if len(all_events) > 1:
                            # Find the index of current event in full history
                            current_event_idx = None
                            for idx, event in enumerate(all_events):
                                if (
                                    event.ts == row.ts
                                    and event.host_address == row.host_address
                                    and event.latency_ms == row.latency_ms
                                ):
                                    current_event_idx = idx
                                    break

                            # Look for previous event with host_address
                            if current_event_idx is not None and current_event_idx > 0:
                                for j in range(current_event_idx - 1, -1, -1):
                                    if all_events[j].host_address:
                                        prev_ip = all_events[j].host_address
                                        break

                        # Extract hostname and IP from host_address (format: "hostname (ip)")
                        if " (" in row.host_address and row.host_address.endswith(")"):
                            hostname, ip_part = row.host_address.split(" (", 1)
                            ip = ip_part.rstrip(")")

                            # Check if IP changed
                            if prev_ip and prev_ip != row.host_address:
                                # Extract previous IP for comparison
                                if " (" in prev_ip and prev_ip.endswith(")"):
                                    prev_ip_only = prev_ip.split(" (", 1)[1].rstrip(")")
                                    if ip != prev_ip_only:
                                        # IP changed - highlight in pink
                                        host_str = (
                                            f"{hostname} ([bright_magenta]{ip}[/])"
                                        )
                                    else:
                                        host_str = row.host_address
                                else:
                                    # Previous format different, assume change
                                    host_str = f"{hostname} ([bright_magenta]{ip}[/])"
                            else:
                                host_str = row.host_address
                        else:
                            host_str = row.host_address

                    # Response info
                    if row.error:
                        # Show error in orange/red
                        response_info = f"[orange_red1]{row.error}[/]"
                    else:
                        # Build response info: status code (blue) + bytes + content-type
                        response_parts = []

                        # Status - handle TCP vs HTTP differently
                        if row.content_type == "tcp/connection":
                            # TCP connection result
                            if row.status_code == 0:
                                response_parts.append("[deep_sky_blue1]connected[/]")
                            else:
                                response_parts.append("[orange_red1]failed[/]")
                        else:
                            # HTTP status code in deep blue
                            if row.status_code:
                                response_parts.append(
                                    f"[deep_sky_blue1]{row.status_code}[/]"
                                )

                        # Bytes
                        if row.bytes_read > 0:
                            if row.bytes_read >= 1024:
                                response_parts.append(f"{row.bytes_read/1024:.1f}KB")
                            else:
                                response_parts.append(f"{row.bytes_read}B")

                        # Content type
                        if row.content_type:
                            response_parts.append(format_content_type(row.content_type))

                        response_info = (
                            " ".join(response_parts) if response_parts else ""
                        )

                    # Latency with consistent range-based purple coloring
                    latency_str = ""
                    if row.error is None:
                        # Use centralized latency color function
                        latency_color = get_latency_color(
                            row.latency_ms, min_latency, max_latency, cfg.color_palette
                        )
                        latency_str = f"[{latency_color}]{row.latency_ms:.1f}ms[/]"

                    log_panel.add_row(
                        f"[dim blue]{row.seq}[/]",
                        time_str,
                        host_str,
                        response_info,
                        latency_str,
                        style="green" if not row.error else None,
                    )
                else:
                    # Add empty row to maintain fixed height of exactly 10 rows
                    log_panel.add_row("", "", "", "", "")

            # Calculate log panel height: header + 10 rows + padding
            log_height = 12  # header (1) + 10 rows + panel borders

            layout = Table.grid(expand=True)
            layout.add_row(
                Panel(
                    top_content,
                    title=chart_title,
                    height=top_height + 2,
                    padding=(0, 0),
                )
            )
            layout.add_row(Panel(log_panel, title=stat_text, height=log_height))
            return layout

        # Event-driven UI: No polling, updates only when data arrives or terminal resizes
        # Use auto_refresh=False to disable automatic refresh and manually control updates
        with Live(console=console, auto_refresh=False) as live:
            live.update(render_panel())
            live.refresh()  # Initial render

            last_dims = (console.size.width, console.size.height)
            last_update_time = 0.0
            # Convert refresh_rate to throttle interval: higher refresh_rate = less throttling
            # refresh_rate of 4 Hz = 250ms, but we use smaller intervals for better responsiveness
            update_throttle_ms = max(25, min(200, 1000 / max(1, cfg.refresh_rate)))

            def should_update() -> bool:
                """Light throttling to prevent excessive redraws during data bursts.

                Implements a time-based throttling mechanism to limit UI updates
                based on the configured refresh rate. This prevents performance
                issues during high-frequency data arrival while maintaining
                responsive UI updates.

                Returns:
                    bool: True if enough time has passed since last update
                """
                nonlocal last_update_time
                current_time = time.time() * 1000  # Convert to milliseconds
                if current_time - last_update_time >= update_throttle_ms:
                    last_update_time = current_time
                    return True
                return False

            def check_and_handle_resize():
                """Check for terminal resize and update UI if dimensions changed.

                Monitors terminal dimensions and triggers UI redraw when the user
                resizes their terminal window. This ensures the chart and layout
                adapt properly to the new size without user intervention.

                Side Effects:
                    - Updates last_dims tracking variable
                    - Triggers UI redraw if size changed and throttling allows
                """
                nonlocal last_dims
                current_dims = (console.size.width, console.size.height)
                if current_dims != last_dims:
                    last_dims = current_dims
                    if should_update():
                        live.update(render_panel())
                        live.refresh()

            try:
                async for r in results_aiter:
                    await handle_result(r)

                    # Check for resize before updating (non-blocking)
                    check_and_handle_resize()

                    # Update UI only when new data arrives and throttling allows
                    if should_update():
                        live.update(render_panel())
                        live.refresh()

                    if cfg.count and r.seq >= cfg.count:
                        break
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                pass

        # Print summary after interactive session
        s = metrics.summary()
        console.print(
            f"--- {cfg.url} sping summary ---\n"
            f"{s['count']} probes, {s['ok']} ok, {s['errors']} errors\n"
            f"Latency (ms): min {s['min']:.3f} mean {s['mean']:.3f} max {s['max']:.3f}"
        )
        return 0

    finally:
        # Clean up file handle
        if export_file_handle:
            export_file_handle.close()


app = typer.Typer()


def version_callback(value: bool):
    """Callback function for the --version command line option.

    When the --version flag is provided, this callback displays the current
    sping version and exits the program immediately. Used by typer's option
    callback mechanism.

    Args:
        value: Boolean indicating if --version flag was provided

    Raises:
        typer.Exit: Always exits after displaying version (if value is True)
    """
    if value:
        console = Console()
        console.print(f"sping version {__version__}")
        raise typer.Exit()


@app.command()
def main(
    url: str = typer.Argument(..., help="URL to probe"),
    interval: float = typer.Option(1.0, help="Interval between probes in seconds"),
    count: Optional[int] = typer.Option(None, help="Number of probes to send"),
    timeout: float = typer.Option(10.0, help="Request timeout in seconds"),
    method: str = typer.Option("HEAD", help="HTTP method to use"),
    json_output: bool = typer.Option(False, "--json", help="JSON output mode"),
    plain: bool = typer.Option(False, "--plain", help="Plain text output mode"),
    body: bool = typer.Option(False, "--body", help="Include full body transfer time"),
    no_keepalive: bool = typer.Option(
        False, "--no-keepalive", help="Disable persistent connections"
    ),
    resolve_once: bool = typer.Option(
        False, "--resolve-once", help="Resolve DNS only once"
    ),
    user_agent: Optional[str] = typer.Option(
        None, "--user-agent", help="Custom User-Agent string"
    ),
    auth: Optional[str] = typer.Option(
        None, "--auth", help="Authentication: user:pass or bearer:token"
    ),
    insecure: bool = typer.Option(False, "--insecure", help="Skip TLS verification"),
    warn: Optional[float] = typer.Option(
        None, "--warn", help="Warning threshold in ms"
    ),
    crit: Optional[float] = typer.Option(
        None, "--crit", help="Critical threshold in ms"
    ),
    export_file: Optional[str] = typer.Option(
        None, "--export-file", help="Export JSON results to file"
    ),
    percentiles: bool = typer.Option(
        False, "--percentiles", help="Show percentiles in summary"
    ),
    refresh_rate: float = typer.Option(
        4.0,
        "--refresh-rate",
        help="UI update throttling in Hz (higher = more responsive, lower = less CPU)",
    ),
    palette: ColorPalette = typer.Option(
        ColorPalette.SUNSET,
        "--palette",
        help="Color palette: sunset (warm oranges/reds), ocean (blues/teals), forest (greens), volcano (reds/oranges), galaxy (purples/magentas), arctic (cool blues/whites), neon (bright electric), monochrome (grays)",
    ),
    ipv4: bool = typer.Option(False, "--ipv4", help="Force IPv4 only"),
    ipv6: bool = typer.Option(False, "--ipv6", help="Force IPv6 only"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show version and exit"
    ),
) -> None:
    """Main entry point for the sping CLI application.

    This function serves as the primary command-line interface, handling argument
    parsing, validation, configuration creation, and application startup. It processes
    all command-line options, validates conflicting settings, normalizes the target URL,
    and launches the appropriate monitoring mode.

    The function supports three distinct output modes:
    - Interactive (default): Real-time terminal UI with charts and logs
    - JSON: Machine-readable structured output for each probe
    - Plain: Human-readable text output for each probe

    Args:
        url: Target URL or hostname to monitor (HTTP/HTTPS/TCP)
        interval: Time between probes in seconds (default: 1.0)
        count: Maximum number of probes to send (None = infinite)
        timeout: Request timeout in seconds (default: 10.0)
        method: HTTP method for requests (default: HEAD)
        json_output: Enable JSON output mode for machine parsing
        plain: Enable plain text output mode for simple logging
        body: Include response body transfer time in measurements
        no_keepalive: Disable HTTP persistent connections
        resolve_once: Resolve DNS only once at startup
        user_agent: Custom User-Agent header for HTTP requests
        auth: Authentication credentials (user:pass or bearer:token)
        insecure: Skip TLS certificate verification
        warn: Warning threshold in milliseconds for exit codes
        crit: Critical threshold in milliseconds for exit codes
        export_file: File path to export JSON results
        percentiles: Include percentile statistics in summary
        refresh_rate: UI update frequency in Hz (1-60)
        palette: Color scheme for charts and UI elements
        ipv4: Force IPv4-only resolution
        ipv6: Force IPv6-only resolution
        version: Show version information and exit

    Raises:
        typer.Exit: On validation errors, conflicts, or when thresholds exceeded

    Exit Codes:
        0: Success, no threshold violations
        1: Warning threshold exceeded
        2: Critical threshold exceeded
    """
    # Validate conflicting options
    if ipv4 and ipv6:
        console = Console()
        console.print("[red]Error: --ipv4 and --ipv6 cannot be used together[/]")
        raise typer.Exit(1)

    # Preprocess URL - add http:// if no scheme provided
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"http://{url}"
    elif parsed.scheme == "tcp":
        # Validate TCP URL format
        if not parsed.hostname or not parsed.port:
            console = Console()
            console.print(
                "[red]Error: TCP URLs must include both hostname and port (e.g., tcp://example.com:80)[/]"
            )
            raise typer.Exit(1)

    # Determine mode
    if json_output:
        mode = "json"
    elif plain:
        mode = "plain"
    else:
        mode = "interactive"

    cfg = Config(
        url=url,
        interval=interval,
        count=count,
        timeout=timeout,
        method=method.upper(),
        include_body=body,
        mode=mode,
        keepalive=not no_keepalive,
        resolve_once=resolve_once,
        user_agent=user_agent,
        auth=auth,
        insecure=insecure,
        warn_threshold=warn,
        crit_threshold=crit,
        export_file=export_file,
        show_percentiles=percentiles,
        ipv4_only=ipv4,
        ipv6_only=ipv6,
        refresh_rate=refresh_rate,
        color_palette=palette,
    )

    exit_code = asyncio.run(run(cfg))
    if exit_code:
        raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()

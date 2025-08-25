# service-ping (sping)

Modern terminal HTTP/TCP latency monitoring tool with real-time visualization. Think `httping` meets modern CLI design with rich terminal UI, phase timing, and advanced analytics.

**Status**: Feature-complete MVP with HTTP/TCP support, phase timing, outlier detection, and comprehensive monitoring capabilities.

## Features

- 🌐 **HTTP & TCP Monitoring**: Support for `http://`, `https://`, and `tcp://` protocols
- 📊 **Real-time Visualization**: Interactive charts and live statistics in your terminal
- 🔍 **Phase Breakdown**: DNS, connection, TLS, request, and response timing
- 🚨 **Outlier Detection**: Automatic outlier detection using MAD (Median Absolute Deviation)
- ⚠️ **Threshold Alerting**: Warning and critical thresholds with exit codes
- 🌍 **DNS Control**: IPv4/IPv6 selection and DNS resolution caching
- 📈 **Advanced Statistics**: Percentiles (p50, p90, p95, p99), standard deviation
- 💾 **Multiple Output Formats**: Interactive UI, plain text, JSON, and JSON export
- 🔐 **Authentication**: Bearer tokens and basic auth support
- 🎨 **Rich Terminal UI**: Beautiful charts, color-coded logs, and responsive layouts
- 🌈 **Color Palettes**: Choose from 8 themed color schemes (sunset, ocean, forest, volcano, galaxy, arctic, neon, monochrome)

## Demo

<img src="https://gitlab.com/dseltzer/sping/-/raw/master/demo/sping-graph-demo.gif" alt="sping Interactive Demo" width="50%">

*Real-time latency monitoring with interactive charts showing HTTP response times, outlier detection, and live statistics.*

## Install

```bash
pip install service-ping-sping
```

For development:
```bash
pip install -e .[dev]
```

## Quick Start

```bash
# HTTP monitoring with interactive UI
sping google.com

# TCP connection monitoring
sping tcp://google.com:80

# HTTPS with custom options
sping https://api.example.com --interval 0.5 --count 20

# JSON output for automation
sping google.com --json --count 5

# Advanced monitoring with thresholds
sping example.com --warn 100 --crit 500 --percentiles

# Try different color themes
sping example.com --palette ocean
```

## Usage Examples

### HTTP/HTTPS Monitoring
```bash
# Basic HTTP monitoring (auto-adds http://)
sping example.com

# HTTPS with custom method and body transfer
sping https://api.example.com --method POST --body

# IPv4 only with DNS caching
sping google.com --ipv4 --resolve-once

# With authentication
sping api.example.com --auth "bearer:your-token"
sping api.example.com --auth "user:password"
```

### TCP Connection Monitoring
```bash
# Test TCP connectivity
sping tcp://google.com:80
sping tcp://example.com:443

# Monitor database connections
sping tcp://localhost:5432 --interval 0.1
```

### Advanced Features
```bash
# Outlier detection and thresholds
sping example.com --warn 100 --crit 500 --count 100

# Export detailed timing data
sping example.com --export-file results.json --count 50

# Show percentile statistics
sping example.com --percentiles --count 100

# Plain output for scripting
sping example.com --plain --count 5
```

## Outlier Detection

sping automatically detects unusual latency spikes using **Median Absolute Deviation (MAD)** analysis:

### What Counts as an Outlier
- **Latency outliers**: Response times that deviate significantly from recent baseline performance
- **Statistical threshold**: Latencies that are more than **6x the MAD** away from the median
- **Baseline requirement**: Needs at least 10 successful samples to establish baseline  
- **Rolling window**: Uses the last 30 successful requests to calculate normal behavior
- **Successful requests only**: Only analyzes successful responses (errors are tracked separately)

### How It Works
1. **Baseline calculation**: Median of recent 30 successful latencies (e.g., 100ms)
2. **Variability measure**: MAD of those latencies (e.g., 15ms)  
3. **Outlier threshold**: `|current_latency - median| / MAD > 6.0`
4. **Example**: If baseline is 100ms ± 15ms MAD, requests > 190ms or < 10ms would be outliers

### Visual Indicators
- **Interactive mode**: Outlier requests show `[OUTLIER]` marker in the log
- **Statistics bar**: Shows red outlier count when detected (e.g., `outliers 3`)
- **JSON output**: `"anomaly": true` field in export data (kept for API compatibility)

*Note: Outlier detection helps identify performance degradation, network issues, or service problems that might not trigger error thresholds.*

## Command Line Options

### Core Options
- `-i, --interval FLOAT`: Seconds between probes (default: 1.0)
- `-c, --count INT`: Number of probes then exit
- `--timeout FLOAT`: Request timeout in seconds (default: 10.0)
- `-X, --method TEXT`: HTTP method (default: HEAD)

### Protocol & DNS
- `--ipv4`: Force IPv4 only
- `--ipv6`: Force IPv6 only  
- `--resolve-once`: Resolve DNS only once and cache

### HTTP Options
- `--body`: Include full body transfer time
- `--no-keepalive`: Disable persistent connections
- `--user-agent TEXT`: Custom User-Agent string
- `--auth TEXT`: Authentication (user:pass or bearer:token)
- `--insecure`: Skip TLS verification

### Monitoring & Alerts
- `--warn FLOAT`: Warning threshold in milliseconds
- `--crit FLOAT`: Critical threshold in milliseconds
- `--percentiles`: Show percentile statistics in summary

### UI & Display
- `--refresh-rate FLOAT`: UI update throttling in Hz (default: 4.0, higher = more responsive, lower = less CPU)
- `--palette PALETTE`: Color palette for latency visualization (default: sunset)
- `--xterm-colors-only`: Force basic terminal color compatibility (useful for older terminals)

### Color Palettes

Choose from beautiful themed color palettes to customize your latency visualization:

#### Sunset Palette (Default)
*Warm oranges and reds reminiscent of a beautiful sunset*

`#626262` `#808080` `#6B59C3` `#836FFF` `#8968CD` `#AB82FF` `#CD96CD` `#FFBBFF` `#CD8C95` `#FFAEB9`

<details>
<summary><strong>View All Color Palettes</strong></summary>

#### Ocean Palette
*Cool blues and teals like ocean depths*

`#000080` `#0000FF` `#1874CD` `#1E90FF` `#009ACD` `#00BFFF` `#00CDCD` `#00FFFF` `#66CDAA` `#7FFFD4`

#### Forest Palette
*Natural greens from deep forest to bright sunlight*

`#BC8F8F` `#D2B48C` `#F4A460` `#A2CD5A` `#BCEE68` `#006400` `#008B00` `#00CD00` `#00FF00` `#66FF66`

#### Volcano Palette
*Fiery reds and oranges like molten lava*

`#8B0000` `#CD0000` `#FF0000` `#FF4500` `#CD6600` `#FF8C00` `#FFA500` `#CDAD00` `#FFD700` `#FFFF66`

#### Galaxy Palette
*Cosmic purples and magentas of deep space*

`#551A8B` `#7D26CD` `#AB82FF` `#CD00CD` `#EE00EE` `#FF00FF` `#CD6090` `#FF1493` `#CD919E` `#FF00FF`

#### Arctic Palette
*Crisp blues and whites of polar ice*

`#4682B4` `#A2B5CD` `#CAE1FF` `#E0EEEE` `#E0FFFF` `#FFFFFF` `#8DB6CD` `#B0E2FF` `#87CEEB` `#FFFFFF`

#### Neon Palette
*Bright electric colors for a cyberpunk feel*

`#1C1C1C` `#4D4D4D` `#0000FF` `#1E90FF` `#00FFFF` `#00FF7F` `#7FFF00` `#FFFF00` `#FF1493` `#FF00FF`

#### Monochrome Palette
*Classic grayscale gradient*

`#121212` `#262626` `#3A3A3A` `#4D4D4D` `#626262` `#808080` `#9E9E9E` `#B2B2B2` `#D6D6D6` `#EDEDED`

</details>

```bash
# Examples with different palettes
sping example.com --palette ocean
sping example.com --palette volcano --count 20
sping example.com --palette neon --percentiles
```

#### Color Compatibility Notes

**Terminal Color Support**: sping automatically detects your terminal's color capabilities and adjusts accordingly. However, older terminals or certain environments may experience:

- **Limited Color Support**: Older terminals may only support basic ANSI colors rather than rich RGB colors
- **Solution**: Set `TERM=xterm-256color` in your environment or use `--xterm-colors-only` for consistent basic colors
- **Compatibility Mode**: Use `--xterm-colors-only` to force basic terminal colors that work everywhere

```bash
# For maximum compatibility with older terminals
sping example.com --xterm-colors-only

# Or set environment variable for better color support
TERM=xterm-256color sping example.com
```

### Output Formats
- `--json`: JSON output mode (one object per line)
- `--plain`: Plain text output mode
- `--export-file FILE`: Export JSON results to file

## Output Formats

### Interactive Mode (Default)
Real-time terminal UI with:
- Live latency chart with gradient coloring
- Recent requests log with timing details
- Statistics panel with min/mean/max/stdev
- Outlier highlighting and threshold indicators

### Plain Text Mode (`--plain`)
```
[1] 1755658486.287: 484.313ms 200 (application/json) from httpbin.org (52.1.207.236)
--- https://httpbin.org/get sping summary ---
1 probes, 1 ok, 0 errors
Latency (ms): min 484.313 mean 484.313 max 484.313
```

### JSON Mode (`--json`)
```json
{"seq": 1, "timestamp": 1755658729.193, "latency_ms": 11.110, "status_code": 0, "error": null, "bytes_read": 0, "content_type": "tcp/connection", "host_address": "google.com (142.250.65.238)", "anomaly": false, "phases": {"dns_ms": 5.444, "connect_ms": 5.598, "tls_ms": null, "request_write_ms": null, "ttfb_ms": null, "body_read_ms": null, "total_ms": 11.110}}
```

## Phase Timing Breakdown

sping provides detailed timing for each phase of the connection:

- **DNS**: Domain name resolution time
- **Connect**: TCP connection establishment  
- **TLS**: TLS/SSL handshake time (HTTPS only)
- **Request Write**: Time to send HTTP request
- **TTFB**: Time to first byte (response headers)
- **Body Read**: Time to read response body
- **Total**: End-to-end request time

## Exit Codes

- `0`: Success
- `1`: Warning threshold exceeded (when `--warn` specified)
- `2`: Critical threshold exceeded (when `--crit` specified)

Perfect for monitoring scripts and alerting systems.

## Quit Interactive Mode

Press `Ctrl+C` to gracefully exit and see the final summary.

## Requirements

- Python 3.9+
- Modern terminal with color support recommended
- Works on Linux, macOS, and Windows

## License

MIT - see [LICENSE.md](https://gitlab.com/dseltzer/sping/-/blob/master/LICENSE.md)

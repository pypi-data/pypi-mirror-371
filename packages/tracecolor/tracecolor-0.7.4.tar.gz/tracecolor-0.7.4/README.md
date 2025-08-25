# tracecolor

Enhanced Python logger with colorized output, TRACE/PROGRESS levels, UDP monitoring, and file logging. Powered by Loguru backend for superior performance and features.

## Features

### Core Features
- Custom TRACE logging level (lower than DEBUG)
- Custom PROGRESS logging level (between DEBUG and INFO)
- Colorized output for different log levels
- Rate-limiting for PROGRESS messages (once per second per call site)
- Simple and clean API

### Enhanced Features (v0.7.0)
- **Pure Loguru Backend**: Superior performance and features
- **UDP Remote Monitoring**: Real-time log streaming with `tracecolor-monitor` command
- **File Logging**: Automatic rotation, compression, and retention
- **External Configuration**: JSON/YAML configuration files
- **Multiple Destinations**: Simultaneous logging to console, file, and UDP
- **Automatic Dependencies**: Loguru installed automatically with pip install
- **Console Script**: `tracecolor-monitor` available globally after installation
- **Enterprise Ready**: Thread-safe, async support, production-grade

## Installation

```bash
pip install tracecolor
```

This automatically installs:
- `loguru` - Advanced logging backend
- `colorlog` - Colorized console output

### Optional Dependencies
```bash
# For YAML configuration support
pip install tracecolor[yaml]

# For development
pip install tracecolor[dev]
```

## Usage

### Basic Usage
```python
from tracecolor import tracecolor

# Create a logger
logger = tracecolor(__name__)

# Log at different levels
logger.trace("Detailed tracing information")
logger.debug("Debugging information")
logger.progress("Progress update information (rate-limited)")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### Enhanced Usage (v0.6.0 Features)
```python
from tracecolor import tracecolor

# Standard usage now automatically uses Loguru backend if available
logger = tracecolor(__name__)  # Now powered by Loguru!
logger.info("Better performance, same API")

# Enhanced features explicitly enabled
logger = tracecolor(
    name=__name__,
    enable_console=True,      # Console output (same as original)
    enable_udp=True,          # UDP remote monitoring
    enable_file=True,         # File logging with rotation
    log_dir="./logs",         # Log directory
    udp_host="127.0.0.1",     # UDP monitoring host
    udp_port=9999             # UDP monitoring port
)

# Same API as original tracecolor
logger.info("This message goes to console, file, AND UDP socket")
logger.progress("Progress messages still rate-limited, now with enterprise backend")

# Alternative: convenience function (same result)
from tracecolor import create_enhanced_logger
logger = create_enhanced_logger(__name__, enable_udp=True, enable_file=True, log_dir="logs")

# Monitor logs in real-time (separate terminal)
# tracecolor-monitor
# or: python -m tracecolor.monitor
```

### External Configuration
```python
# Create logging_config.json
{
    "logging": {
        "enable_console": true,
        "enable_file": true,
        "enable_udp": true,
        "log_dir": "./logs",
        "udp_host": "127.0.0.1",
        "udp_port": 9999,
        "log_level": "INFO"
    }
}

# Use configuration file
from tracecolor import tracecolor
logger = tracecolor(__name__, config_file="logging_config.json")
```

## UDP Remote Monitoring

Monitor logs in real-time from any application using enhanced features:

```bash
# Terminal 1: Run your application with UDP logging
python your_app.py

# Terminal 2: Monitor logs in real-time
python -m tracecolor.monitor

# Or specify host/port
python -m tracecolor.monitor --host 0.0.0.0 --port 8888

# Legacy format also supported
python tracecolor/monitor.py listen 192.168.1.100 9999
```

The monitor displays formatted output with timestamps, log levels, and messages in real-time.

## Migration Guide

### From v0.5.0 to v0.6.0

**Step 1**: Update package (existing code continues to work)
```bash
pip install --upgrade tracecolor
```

**Step 2**: Install enhanced dependencies (optional)
```bash
pip install tracecolor[enhanced]
```

**Step 3**: Optionally enable enhanced features where needed
```python
# Before (still works, now with Loguru backend!)
from tracecolor import tracecolor
logger = tracecolor(__name__)  # Automatically uses Loguru if available

# Enhanced features when needed
logger = tracecolor(__name__, enable_udp=True, enable_file=True, log_dir="logs")
```

**Step 4**: Add external configuration as projects mature
```python
logger = tracecolor(__name__, config_file="logging.json")
```

## Color Scheme

- TRACE: Gray (bold black)
- DEBUG: Cyan
- PROGRESS: Blue
- INFO: Green
- WARNING: Yellow
- ERROR: Red
- CRITICAL: Bold Red

## Examples

See the `examples/` directory for comprehensive usage examples:
- `basic_usage.py` - Original v0.5.0 functionality
- `enhanced_features.py` - New v0.6.0 features and migration guide

## License

MIT
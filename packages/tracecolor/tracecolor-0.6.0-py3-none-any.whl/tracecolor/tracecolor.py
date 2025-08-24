import logging
import colorlog
import time
import inspect
import socket
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, Union
from collections import defaultdict

try:
    from loguru import logger as _loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ProgressRateLimiter:
    """Rate limiter for PROGRESS messages - 1 per second per call site"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.last_times: Dict[str, float] = defaultdict(float)
    
    def should_log(self, call_site: str) -> bool:
        """Check if enough time has passed since last log from this call site"""
        current_time = time.time()
        last_time = self.last_times[call_site]
        
        if current_time - last_time >= self.interval:
            self.last_times[call_site] = current_time
            return True
        return False


class UDPSink:
    """Custom UDP sink for remote monitoring"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9999):
        self.host = host
        self.port = port
        self.sock = None
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception:
            pass  # Silent fail
    
    def write(self, message):
        """Send log message via UDP"""
        if not self.sock:
            return
            
        try:
            record = message.record
            udp_data = {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "logger": record["name"],
                "message": record["message"],
                "function": record["function"],
                "file": record["file"].name,
                "line": record["line"]
            }
            
            json_data = json.dumps(udp_data, ensure_ascii=False)
            self.sock.sendto(json_data.encode('utf-8'), (self.host, self.port))
        except Exception:
            pass  # Silent fail


# TracecolorEnhanced class removed - now tracecolor is the Loguru wrapper


class tracecolor:
    """
    Enhanced logger with colorized output and TRACE/PROGRESS levels.
    Now powered by Loguru backend for better performance and features.
    
    Features:
    - Custom TRACE logging level (5, lower than DEBUG)
    - Custom PROGRESS logging level (15, between DEBUG and INFO)
    - Colorized output for different log levels
    - Rate-limiting for PROGRESS messages (once per second per call site)
    - Loguru backend with enterprise features
    - Optional enhanced features (UDP, file logging, external config)
    
    Usage:
    ```python
    from tracecolor import tracecolor
    
    logger = tracecolor(__name__)
    logger.trace("Detailed trace message")
    logger.debug("Debug information")
    logger.progress("Progress update (rate-limited)")
    logger.info("General information")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical error")
    ```
    """
    TRACE_LEVEL = 5  # TRACE below DEBUG (10)
    PROGRESS_LEVEL = 15  # PROGRESS between DEBUG (10) and INFO (20)
    PROGRESS_INTERVAL: float = 1  # Default interval in seconds for progress messages (0 or less disables rate-limiting for testing)

    def __init__(self, 
                 name: str,
                 enable_console: bool = True,
                 enable_file: bool = False,
                 enable_udp: bool = False,
                 log_dir: Optional[Union[str, Path]] = None,
                 udp_host: str = "127.0.0.1",
                 udp_port: int = 9999,
                 log_level: str = "TRACE",
                 config_file: Optional[str] = None):
        
        self.name = name
        self.progress_limiter = ProgressRateLimiter()
        self.udp_sink = None
        self._logger_id = id(self)  # Unique ID for this logger instance
        
        # Check if Loguru is available, fall back to logging if not
        if LOGURU_AVAILABLE:
            self._init_loguru_backend(enable_console, enable_file, enable_udp, 
                                    log_dir, udp_host, udp_port, log_level, config_file)
        else:
            self._init_logging_backend(name)
    
    def _init_loguru_backend(self, enable_console, enable_file, enable_udp, 
                           log_dir, udp_host, udp_port, log_level, config_file):
        """Initialize with Loguru backend (preferred)"""
        # Load external configuration if provided
        if config_file:
            config = self._load_config(config_file)
            enable_console = config.get("enable_console", enable_console)
            enable_file = config.get("enable_file", enable_file)
            enable_udp = config.get("enable_udp", enable_udp)
            log_dir = config.get("log_dir", log_dir)
            udp_host = config.get("udp_host", udp_host)
            udp_port = config.get("udp_port", udp_port)
            log_level = config.get("log_level", log_level)
        
        # Create a new logger instance to avoid conflicts
        self.logger = _loguru_logger.bind(name=self.name, logger_id=self._logger_id)
        
        # Remove default loguru handler for this instance
        _loguru_logger.remove()
        
        # Add custom PROGRESS level to match tracecolor exactly
        try:
            _loguru_logger.level("PROGRESS", no=15, color="<blue>")
        except TypeError:
            pass  # Level already exists
        
        # Console handler with tracecolor format (backward compatible)
        if enable_console:
            console_format = (
                "<dim>{level.name[0]}</dim> "  # Single char prefix
                "|<dim>{time:YYYY-MM-DD HH:mm:ss.SSS}</dim>| "  # Timestamp with milliseconds
                "<level>{message}</level>"  # Colored message
            )
            
            _loguru_logger.add(
                sink=sys.stderr,
                format=console_format,
                level=log_level,
                colorize=True,
                filter=self._console_filter
            )
        
        # File handler (enhanced feature)
        if enable_file and log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True, parents=True)
            
            file_format = (
                "{level.name[0]} |{time:YYYY-MM-DD HH:mm:ss.SSS}| "
                "[{name}:{function}:{line}] {message}"
            )
            
            _loguru_logger.add(
                sink=str(log_path / f"{self.name}.log"),
                format=file_format,
                level=log_level,
                rotation="10 MB",
                retention="7 days",
                compression="zip",
                filter=lambda record: record["extra"].get("logger_id") == self._logger_id
            )
        
        # UDP handler for remote monitoring (enhanced feature)
        if enable_udp:
            try:
                self.udp_sink = UDPSink(udp_host, udp_port)
                _loguru_logger.add(
                    sink=self.udp_sink,
                    level=log_level,
                    format="{message}",
                    filter=lambda record: record["extra"].get("logger_id") == self._logger_id
                )
            except Exception:
                pass  # Silent fail
        
        # Bind the logger to this instance with unique ID
        self.logger = _loguru_logger.bind(name=self.name, logger_id=self._logger_id)
        self.backend = "loguru"
    
    def _init_logging_backend(self, name):
        """Fallback to original logging backend if Loguru not available"""
        import logging
        import colorlog
        
        self.logger = logging.getLogger(name)
        
        # Register custom levels
        logging.addLevelName(self.TRACE_LEVEL, "TRACE")
        logging.addLevelName(self.PROGRESS_LEVEL, "PROGRESS")

        # Set up color formatter for standard log levels
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname).1s%(reset)s |%(asctime)s.%(msecs)03d| %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
                'TRACE': 'bold_black',  # Use bold_black for gray
                'PROGRESS': 'blue',
            }
        )

        # Console handler for standard log levels
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Set the logger level to the lowest to capture all messages
        self.logger.setLevel(self.TRACE_LEVEL)
        self.logger.propagate = False

        # Initialize last log time for rate-limiting
        self._last_progress_log_times = {}
        self.backend = "logging"
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON or YAML file"""
        config_path = Path(config_file)
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_file.endswith(('.yaml', '.yml')):
                    if not YAML_AVAILABLE:
                        raise ImportError("PyYAML required for YAML config files")
                    return yaml.safe_load(f).get('logging', {})
                else:
                    return json.load(f).get('logging', {})
        except Exception:
            return {}
    
    def _console_filter(self, record):
        """Filter for console output - handles progress rate limiting (Loguru backend)"""
        # Only process records from this logger instance
        if record["extra"].get("logger_id") != self._logger_id:
            return False
        
        # Apply rate limiting only to PROGRESS level
        if record["level"].name == "PROGRESS":
            call_site = f"{record['file'].name}:{record['function']}:{record['line']}"
            if not self.progress_limiter.should_log(call_site):
                return False  # Skip this message
        
        return True  # Allow all other messages

    def trace(self, message, *args, **kwargs):
        """Log a message with severity 'TRACE'."""
        if self.backend == "loguru":
            self.logger.trace(message, *args, **kwargs)
        else:
            if self.logger.level <= self.TRACE_LEVEL:
                self.logger.log(self.TRACE_LEVEL, message, *args, **kwargs)

    def progress(self, message, *args, **kwargs):
        """Log a message with severity 'PROGRESS' (for progress updates, rate-limited per call site)."""
        if self.backend == "loguru":
            # Loguru backend handles rate limiting via filter
            self.logger.log("PROGRESS", message, *args, **kwargs)
        else:
            # Original logging backend with rate limiting
            # First, check if the logger is even enabled for the PROGRESS level.
            if not self.logger.isEnabledFor(self.PROGRESS_LEVEL):
                return

            # If PROGRESS_INTERVAL is non-positive, log directly and bypass rate-limiting
            if self.PROGRESS_INTERVAL <= 0:
                # Directly call _log as per instruction, handling relevant kwargs
                exc_info_val = kwargs.get('exc_info')
                extra_val = kwargs.get('extra')
                stack_info_val = kwargs.get('stack_info', False)
                # stacklevel=2 ensures findCaller in _log points to the caller of progress()
                self.logger._log(self.PROGRESS_LEVEL, message, args, exc_info=exc_info_val, extra=extra_val, stack_info=stack_info_val, stacklevel=2)
                return

            # Per-call-site rate-limiting logic
            try:
                # Get the frame of the caller of this progress() method
                current_frame = inspect.currentframe()
                if current_frame and current_frame.f_back:
                    frame = current_frame.f_back
                    call_site_key = (frame.f_code.co_filename, frame.f_lineno)
                else:
                    # Fallback if frame inspection is not possible (e.g., no caller frame)
                    call_site_key = "__global_progress_no_caller_frame__"
            except Exception: # Catch any other unexpected errors during inspection
                # Fallback to a different global key if inspect raises an unexpected exception
                call_site_key = "__global_progress_inspect_exception__"

            current_time = time.time()
            # Get the last log time for this specific call site, default to 0 if not found
            last_log_time_for_site = self._last_progress_log_times.get(call_site_key, 0)

            # Log only if a second has passed since the last log from this specific call site
            if current_time - last_log_time_for_site >= self.PROGRESS_INTERVAL:
                self._last_progress_log_times[call_site_key] = current_time
                # Actually log the message using the base Logger's log method
                self.logger.log(self.PROGRESS_LEVEL, message, *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        """Log a message with severity 'DEBUG'."""
        if self.backend == "loguru":
            self.logger.debug(message, *args, **kwargs)
        else:
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Log a message with severity 'INFO'."""
        if self.backend == "loguru":
            self.logger.info(message, *args, **kwargs)
        else:
            if self.logger.level <= logging.INFO:
                self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log a message with severity 'WARNING'."""
        if self.backend == "loguru":
            self.logger.warning(message, *args, **kwargs)
        else:
            if self.logger.level <= logging.WARNING:
                self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log a message with severity 'ERROR'."""
        if self.backend == "loguru":
            self.logger.error(message, *args, **kwargs)
        else:
            if self.logger.level <= logging.ERROR:
                self.logger.error(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Log a message with severity 'CRITICAL'."""
        if self.backend == "loguru":
            self.logger.critical(message, *args, **kwargs)
        else:
            if self.logger.level <= logging.CRITICAL:
                self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message, *args, **kwargs):
        """Log exception with traceback"""
        if self.backend == "loguru":
            self.logger.exception(message, *args, **kwargs)
        else:
            self.logger.exception(message, *args, **kwargs)

# Factory functions for enhanced features

def create_enhanced_logger(name: str, 
                          enable_console: bool = True,
                          enable_file: bool = False,
                          enable_udp: bool = False,
                          log_dir: Optional[Union[str, Path]] = None,
                          udp_host: str = "127.0.0.1", 
                          udp_port: int = 9999,
                          log_level: str = "TRACE",
                          config_file: Optional[str] = None) -> 'tracecolor':
    """
    Create enhanced tracecolor logger with Loguru backend features enabled
    
    This is just a convenience function that enables enhanced features by default.
    The main tracecolor class now supports all these features natively.
    
    Usage:
        # Basic enhanced usage (Loguru backend + enhanced features)
        logger = create_enhanced_logger(__name__)
        
        # With UDP monitoring and file logging
        logger = create_enhanced_logger(__name__, enable_udp=True, enable_file=True, log_dir="logs")
        
        # With external configuration
        logger = create_enhanced_logger(__name__, config_file="logging.json")
    
    Args:
        name: Logger name (typically __name__)
        enable_console: Enable console output (default: True)
        enable_file: Enable file logging (default: False)
        enable_udp: Enable UDP remote monitoring (default: False)
        log_dir: Directory for log files
        udp_host: UDP host for remote monitoring
        udp_port: UDP port for remote monitoring
        log_level: Minimum log level (default: "TRACE")
        config_file: External configuration file (JSON/YAML)
        
    Returns:
        tracecolor instance with enhanced features enabled
    """
    return tracecolor(
        name=name,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_udp=enable_udp,
        log_dir=log_dir,
        udp_host=udp_host,
        udp_port=udp_port,
        log_level=log_level,
        config_file=config_file
    )


# Backward compatibility: 
# - tracecolor(__name__) uses Loguru backend if available, falls back to logging
# - create_enhanced_logger() is a convenience function for explicit enhanced features
# - Both return the same tracecolor class, just with different default parameters

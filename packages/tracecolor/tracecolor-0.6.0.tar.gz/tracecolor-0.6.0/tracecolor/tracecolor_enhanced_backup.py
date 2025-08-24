#!/usr/bin/env python3
"""
Tracecolor Enhanced - Loguru-powered logger with backward compatibility

This module provides a drop-in replacement for the original tracecolor logger,
now powered by Loguru backend for enterprise features while maintaining 
the exact same API and behavior.

Features identical to tracecolor 0.5.0:
- TRACE (5), DEBUG (10), PROGRESS (15), INFO (20), WARNING (30), ERROR (40), CRITICAL (50)
- Exact color scheme and single-char prefixes (T, D, P, I, W, E, C)
- Progress rate limiting (1 message per second per call site)
- Timestamp with milliseconds format
- Same API and interface

New features in 0.6.0:
- UDP remote monitoring for real-time log streaming
- File logging with rotation, compression, retention
- External configuration support (JSON/YAML)
- Thread-safe Loguru backend
- Multiple simultaneous sinks
"""

import time
import socket
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, Union
from collections import defaultdict

try:
    from loguru import logger
except ImportError:
    raise ImportError(
        "Tracecolor Enhanced requires Loguru. Install with: pip install loguru>=0.7.2"
    )

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


class TracecolorLogger:
    """
    Tracecolor-compatible logger using Loguru backend
    
    Provides exact same interface and behavior as original tracecolor:
    - Same log levels and colors
    - Progress rate limiting 
    - Single character prefixes
    - Millisecond timestamps
    - Plus UDP remote monitoring and file logging
    """
    
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
        self.logger = logger.bind(name=name, logger_id=self._logger_id)
        
        # Remove default loguru handler for this instance
        logger.remove()
        
        # Add custom PROGRESS level to match tracecolor exactly
        try:
            logger.level("PROGRESS", no=15, color="<blue>")
        except TypeError:
            pass  # Level already exists
        
        # Console handler with tracecolor format
        if enable_console:
            console_format = (
                "<dim>{level.name[0]}</dim> "  # Single char prefix
                "|<dim>{time:YYYY-MM-DD HH:mm:ss.SSS}</dim>| "  # Timestamp with milliseconds
                "<level>{message}</level>"  # Colored message
            )
            
            logger.add(
                sink=sys.stderr,
                format=console_format,
                level=log_level,
                colorize=True,
                filter=self._console_filter
            )
        
        # File handler
        if enable_file and log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True, parents=True)
            
            file_format = (
                "{level.name[0]} |{time:YYYY-MM-DD HH:mm:ss.SSS}| "
                "[{name}:{function}:{line}] {message}"
            )
            
            logger.add(
                sink=str(log_path / f"{name}.log"),
                format=file_format,
                level=log_level,
                rotation="10 MB",
                retention="7 days",
                compression="zip",
                filter=lambda record: record["extra"].get("logger_id") == self._logger_id
            )
        
        # UDP handler for remote monitoring
        if enable_udp:
            try:
                self.udp_sink = UDPSink(udp_host, udp_port)
                logger.add(
                    sink=self.udp_sink,
                    level=log_level,
                    format="{message}",
                    filter=lambda record: record["extra"].get("logger_id") == self._logger_id
                )
            except Exception:
                pass  # Silent fail
        
        # Bind the logger to this instance with unique ID
        self.logger = logger.bind(name=name, logger_id=self._logger_id)
    
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
        """Filter for console output - handles progress rate limiting"""
        # Only process records from this logger instance
        if record["extra"].get("logger_id") != self._logger_id:
            return False
        
        # Apply rate limiting only to PROGRESS level
        if record["level"].name == "PROGRESS":
            call_site = f"{record['file'].name}:{record['function']}:{record['line']}"
            if not self.progress_limiter.should_log(call_site):
                return False  # Skip this message
        
        return True  # Allow all other messages
    
    # Tracecolor-compatible interface
    def trace(self, message: str, *args, **kwargs):
        """Log TRACE level message (most detailed)"""
        self.logger.trace(message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log DEBUG level message"""
        self.logger.debug(message, *args, **kwargs)
    
    def progress(self, message: str, *args, **kwargs):
        """Log PROGRESS level message (rate-limited to 1/second per call site)"""
        self.logger.log("PROGRESS", message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log INFO level message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log WARNING level message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log ERROR level message"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log CRITICAL level message"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, *args, **kwargs)


# Factory function for drop-in replacement
def tracecolor(name: str, 
               enable_console: bool = True,
               enable_file: bool = False,
               enable_udp: bool = False,
               log_dir: Optional[Union[str, Path]] = None,
               udp_host: str = "127.0.0.1", 
               udp_port: int = 9999,
               log_level: str = "TRACE",
               config_file: Optional[str] = None) -> TracecolorLogger:
    """
    Drop-in replacement for tracecolor with enhanced features
    
    Usage:
        # Exact same as original tracecolor
        logger = tracecolor(__name__)
        
        # With enhanced features
        logger = tracecolor(__name__, enable_udp=True, enable_file=True, log_dir="logs")
        
        # With external configuration
        logger = tracecolor(__name__, config_file="logging.json")
    
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
        TracecolorLogger instance with same interface as original tracecolor
    """
    return TracecolorLogger(
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
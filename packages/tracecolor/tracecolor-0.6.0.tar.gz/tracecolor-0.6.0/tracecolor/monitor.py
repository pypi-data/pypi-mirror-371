#!/usr/bin/env python3
"""
Tracecolor UDP Monitor - Real-time log monitoring over UDP

This module provides a UDP log monitor for real-time viewing of logs
from tracecolor-enhanced applications with UDP logging enabled.

Usage:
    # As module
    python -m tracecolor.monitor
    python -m tracecolor.monitor --host 0.0.0.0 --port 8888
    
    # Direct execution
    python monitor.py
    python monitor.py listen 192.168.1.100 9999
"""

import socket
import json
import argparse
import sys
from typing import Dict


def udp_monitor(host: str = "127.0.0.1", port: int = 9999):
    """
    UDP log monitor with tracecolor-style output
    
    Args:
        host: Host to bind to (default: "127.0.0.1")
        port: Port to bind to (default: 9999)
    """
    print(f"Tracecolor UDP Monitor v0.6.0")
    print(f"Listening on {host}:{port}")
    print("Press Ctrl+C to stop\n")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
    except OSError as e:
        print(f"ERROR: Cannot bind to {host}:{port} - {e}")
        print("Try a different port or check if another process is using this port")
        return
    
    # Level color mapping (same as tracecolor)
    level_colors = {
        'TRACE': '\033[1;30m',     # Gray (dim)
        'DEBUG': '\033[36m',       # Cyan  
        'PROGRESS': '\033[34m',    # Blue
        'INFO': '\033[32m',        # Green
        'SUCCESS': '\033[32m',     # Green (Loguru level)
        'WARNING': '\033[33m',     # Yellow
        'ERROR': '\033[31m',       # Red
        'CRITICAL': '\033[1;31m',  # Bright Red
    }
    reset = '\033[0m'
    
    message_count = 0
    
    try:
        print(f"{'Time':<12} {'Level':<8} {'Logger':<15} {'Location':<25} {'Message'}")
        print("-" * 100)
        
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                message_count += 1
                
                try:
                    msg = json.loads(data.decode('utf-8'))
                    
                    # Extract message components
                    timestamp = msg.get('timestamp', '')
                    level = msg.get('level', 'INFO')
                    logger_name = msg.get('logger', 'unknown')
                    message = msg.get('message', '')
                    function = msg.get('function', '')
                    filename = msg.get('file', '')
                    line = msg.get('line', '')
                    
                    # Format timestamp (HH:MM:SS only)
                    time_part = timestamp[11:19] if len(timestamp) > 19 else timestamp
                    
                    # Format location
                    location = f"{filename}:{function}:{line}" if filename else ""
                    if len(location) > 25:
                        location = location[:22] + "..."
                    
                    # Format logger name
                    if len(logger_name) > 15:
                        logger_name = logger_name[:12] + "..."
                    
                    # Format message
                    if len(message) > 50:
                        display_message = message[:47] + "..."
                    else:
                        display_message = message
                    
                    # Apply colors
                    color = level_colors.get(level, '')
                    level_char = level[0]  # Single character
                    
                    # Print formatted message
                    print(f"{time_part:<12} {color}{level_char}{reset} {level[1:]:<7} "
                          f"{logger_name:<15} {location:<25} {display_message}")
                    
                except json.JSONDecodeError:
                    print(f"[{message_count:04d}] Invalid JSON from {addr}: {data[:50]}...")
                except UnicodeDecodeError:
                    print(f"[{message_count:04d}] Invalid UTF-8 from {addr}: {data[:50]}...")
                except Exception as e:
                    print(f"[{message_count:04d}] Error processing message from {addr}: {e}")
                    
            except socket.timeout:
                continue
            except ConnectionResetError:
                # Windows specific - ignore
                continue
                
    except KeyboardInterrupt:
        print(f"\n\nReceived {message_count} messages")
        print("UDP Monitor stopped")
    except Exception as e:
        print(f"Monitor error: {e}")
    finally:
        sock.close()


def main():
    """Main entry point for the UDP monitor"""
    parser = argparse.ArgumentParser(
        description="Tracecolor UDP Monitor - Real-time log monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tracecolor.monitor                    # Monitor localhost:9999
  python -m tracecolor.monitor --port 8888        # Monitor localhost:8888  
  python -m tracecolor.monitor --host 0.0.0.0     # Monitor all interfaces:9999
  python -m tracecolor.monitor --host 192.168.1.100 --port 7777  # Remote monitoring
        """
    )
    
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=9999,
        help='Port to bind to (default: 9999)'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='Tracecolor Monitor v0.6.0'
    )
    
    # Handle legacy command line format for backward compatibility
    if len(sys.argv) > 1 and sys.argv[1] == "listen":
        # Legacy format: python monitor.py listen [host] [port]
        host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 9999
        udp_monitor(host, port)
    else:
        # Standard argparse format
        args = parser.parse_args()
        udp_monitor(args.host, args.port)


if __name__ == "__main__":
    main()
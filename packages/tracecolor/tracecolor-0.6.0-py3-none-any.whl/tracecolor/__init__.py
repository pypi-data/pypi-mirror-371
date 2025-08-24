from .tracecolor import tracecolor, create_enhanced_logger

__version__ = "0.6.0"
__all__ = ['tracecolor', 'create_enhanced_logger']

# Backward compatibility - existing code using tracecolor() continues to work
# Enhanced features now built into tracecolor class with Loguru backend
# create_enhanced_logger() is a convenience function for explicit enhanced features
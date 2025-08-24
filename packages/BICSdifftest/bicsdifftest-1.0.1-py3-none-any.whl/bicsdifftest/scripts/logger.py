"""
Advanced logging system for the differential testing framework.

This module provides comprehensive logging capabilities including
structured logging, performance monitoring, and debug utilities.
"""

import logging
import logging.handlers
import sys
import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import traceback
from contextlib import contextmanager


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    console_output: bool = True
    file_output: bool = True
    
    # File logging options
    log_dir: str = "logs"
    log_file: str = "difftest.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    # Console formatting
    console_format: str = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
    file_format: str = "%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Structured logging
    structured_logging: bool = False
    json_logs: bool = False
    
    # Performance monitoring
    performance_logging: bool = True
    memory_logging: bool = False
    
    # Filtering
    log_filters: Dict[str, LogLevel] = field(default_factory=dict)
    exclude_modules: List[str] = field(default_factory=list)


class StructuredFormatter(logging.Formatter):
    """Structured logging formatter with JSON support."""
    
    def __init__(self, json_format: bool = False):
        super().__init__()
        self.json_format = json_format
        
    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        if self.json_format:
            return self._format_json(record)
        else:
            return self._format_structured(record)
            
    def _format_json(self, record: logging.LogRecord) -> str:
        """Format as JSON."""
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'filename': record.filename,
            'lineno': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'message', 'exc_info', 'exc_text',
                          'stack_info']:
                log_data[key] = value
                
        return json.dumps(log_data)
        
    def _format_structured(self, record: logging.LogRecord) -> str:
        """Format as structured text."""
        base_format = "%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d: %(message)s"
        
        # Add structured fields
        structured_fields = []
        for key, value in record.__dict__.items():
            if key.startswith('field_'):
                field_name = key[6:]  # Remove 'field_' prefix
                structured_fields.append(f"{field_name}={value}")
                
        formatted = base_format % record.__dict__
        
        if structured_fields:
            formatted += " | " + " ".join(structured_fields)
            
        return formatted


class PerformanceMonitor:
    """Performance monitoring utility."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.timers = {}
        self.counters = {}
        self.lock = threading.Lock()
        
    def start_timer(self, name: str) -> str:
        """Start a performance timer."""
        timer_id = f"{name}_{time.time()}"
        with self.lock:
            self.timers[timer_id] = {
                'name': name,
                'start_time': time.perf_counter(),
                'thread': threading.current_thread().name
            }
        return timer_id
        
    def stop_timer(self, timer_id: str) -> Optional[float]:
        """Stop a performance timer and return elapsed time."""
        with self.lock:
            if timer_id in self.timers:
                timer_info = self.timers.pop(timer_id)
                elapsed = time.perf_counter() - timer_info['start_time']
                
                self.logger.info(
                    f"Performance: {timer_info['name']} completed in {elapsed:.3f}s",
                    extra={
                        'field_timer_name': timer_info['name'],
                        'field_elapsed_time': elapsed,
                        'field_thread': timer_info['thread']
                    }
                )
                
                return elapsed
        return None
        
    def increment_counter(self, name: str, value: int = 1):
        """Increment a performance counter."""
        with self.lock:
            self.counters[name] = self.counters.get(name, 0) + value
            
    def get_counter(self, name: str) -> int:
        """Get counter value."""
        with self.lock:
            return self.counters.get(name, 0)
            
    def reset_counters(self):
        """Reset all counters."""
        with self.lock:
            self.counters.clear()
            
    def log_counters(self):
        """Log current counter values."""
        with self.lock:
            for name, value in self.counters.items():
                self.logger.info(
                    f"Counter: {name} = {value}",
                    extra={'field_counter_name': name, 'field_counter_value': value}
                )


class DifftestLogger:
    """
    Advanced logger for differential testing with structured logging,
    performance monitoring, and debug utilities.
    """
    
    def __init__(self, name: str, config: LogConfig = None):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            config: Logging configuration
        """
        self.name = name
        self.config = config or LogConfig()
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.config.level.value)
        
        # Performance monitor
        self.perf_monitor = PerformanceMonitor(self.logger)
        
        # Setup handlers
        self._setup_handlers()
        
        # Context stack for structured logging
        self._context_stack = []
        self._context_lock = threading.Lock()
        
    def _setup_handlers(self):
        """Setup logging handlers."""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        if self.config.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.config.level.value)
            
            if self.config.structured_logging:
                formatter = StructuredFormatter(self.config.json_logs)
            else:
                formatter = logging.Formatter(
                    self.config.console_format,
                    datefmt=self.config.date_format
                )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
        # File handler
        if self.config.file_output:
            log_dir = Path(self.config.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = log_dir / self.config.log_file
            
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count
            )
            file_handler.setLevel(self.config.level.value)
            
            if self.config.structured_logging:
                formatter = StructuredFormatter(self.config.json_logs)
            else:
                formatter = logging.Formatter(
                    self.config.file_format,
                    datefmt=self.config.date_format
                )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        # Apply filters
        for module_pattern, level in self.config.log_filters.items():
            filter_obj = ModuleFilter(module_pattern, level.value)
            for handler in self.logger.handlers:
                handler.addFilter(filter_obj)
                
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
        
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)
        
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with context support."""
        extra = {}
        
        # Add context fields
        with self._context_lock:
            for context in self._context_stack:
                for key, value in context.items():
                    extra[f'field_{key}'] = value
                    
        # Add explicit fields
        for key, value in kwargs.items():
            extra[f'field_{key}'] = value
            
        self.logger.log(level, message, extra=extra)
        
    @contextmanager
    def context(self, **context_fields):
        """Context manager for structured logging."""
        with self._context_lock:
            self._context_stack.append(context_fields)
            
        try:
            yield
        finally:
            with self._context_lock:
                if self._context_stack:
                    self._context_stack.pop()
                    
    @contextmanager
    def timer(self, name: str):
        """Context manager for performance timing."""
        timer_id = self.perf_monitor.start_timer(name)
        try:
            yield
        finally:
            self.perf_monitor.stop_timer(timer_id)
            
    def log_exception(self, message: str = "Exception occurred", **kwargs):
        """Log exception with traceback."""
        exc_info = sys.exc_info()
        if exc_info[0] is not None:
            tb_str = ''.join(traceback.format_exception(*exc_info))
            self.error(f"{message}: {tb_str}", **kwargs)
        else:
            self.error(f"{message}: No active exception", **kwargs)
            
    def log_test_result(self, test_name: str, passed: bool, details: Dict[str, Any] = None):
        """Log test result with structured data."""
        status = "PASS" if passed else "FAIL"
        message = f"Test {test_name}: {status}"
        
        log_data = {
            'test_name': test_name,
            'test_result': status,
            'test_passed': passed
        }
        
        if details:
            log_data.update(details)
            
        if passed:
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)
            
    def log_comparison_result(self, signal_name: str, expected: Any, actual: Any, 
                            passed: bool, error: float = None):
        """Log comparison result."""
        status = "MATCH" if passed else "MISMATCH"
        message = f"Signal {signal_name}: {status}"
        
        log_data = {
            'signal_name': signal_name,
            'expected_value': str(expected),
            'actual_value': str(actual),
            'comparison_passed': passed
        }
        
        if error is not None:
            log_data['error_magnitude'] = error
            
        if passed:
            self.debug(message, **log_data)
        else:
            self.error(message, **log_data)


class ModuleFilter(logging.Filter):
    """Filter for module-specific log levels."""
    
    def __init__(self, module_pattern: str, level: int):
        super().__init__()
        self.module_pattern = module_pattern
        self.level = level
        
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record based on module pattern."""
        if record.name.startswith(self.module_pattern):
            return record.levelno >= self.level
        return True


def setup_logging(config: LogConfig = None) -> DifftestLogger:
    """
    Setup global logging configuration.
    
    Args:
        config: Logging configuration
        
    Returns:
        Main logger instance
    """
    config = config or LogConfig()
    
    # Create main logger
    main_logger = DifftestLogger("BICSdifftest", config)
    
    # Configure third-party loggers
    _configure_third_party_loggers(config)
    
    return main_logger


def _configure_third_party_loggers(config: LogConfig):
    """Configure third-party library loggers."""
    # Cocotb logger
    cocotb_logger = logging.getLogger("cocotb")
    if config.level == LogLevel.DEBUG:
        cocotb_logger.setLevel(logging.DEBUG)
    else:
        cocotb_logger.setLevel(logging.INFO)
        
    # Verilator/subprocess loggers
    for logger_name in ["subprocess", "verilator"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)  # Reduce noise
        
    # Exclude noisy modules if specified
    for module_name in config.exclude_modules:
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.CRITICAL)


# Global logger instance
_global_logger = None


def get_logger(name: str = None) -> DifftestLogger:
    """Get logger instance."""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = setup_logging()
        
    if name:
        return DifftestLogger(name, _global_logger.config)
    else:
        return _global_logger


# Convenience functions
def log_test_start(test_name: str, config: Dict[str, Any] = None):
    """Log test start with configuration."""
    logger = get_logger()
    with logger.context(test_name=test_name, phase="start"):
        logger.info(f"Starting test: {test_name}")
        if config:
            logger.debug("Test configuration", **config)
            

def log_test_complete(test_name: str, result: Dict[str, Any]):
    """Log test completion with results."""
    logger = get_logger()
    with logger.context(test_name=test_name, phase="complete"):
        passed = result.get('passed', False)
        logger.log_test_result(test_name, passed, result)
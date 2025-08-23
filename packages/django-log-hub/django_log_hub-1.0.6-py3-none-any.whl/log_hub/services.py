import logging
from datetime import datetime
import json
import os
from django.conf import settings
from functools import wraps
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class AggregatedLogger:
    """
    Helper class for producing single-line summary logs.
    Maintains the logic of your old code while working without 'with' statement.
    """

    def __init__(
        self,
        logger_name: Optional[str] = None,
        header: Optional[str] = None,
        header_context: Optional[Dict[str, object]] = None,
        separator: str = " | ",
        include_level: bool = False,
        include_timestamp: bool = False,
        auto_log_on_exit: bool = True,
    ) -> None:
        self.logger_name = logger_name or "unknown"
        self.header = header
        self.header_context = header_context or {}
        self.separator = separator
        self.include_level = include_level
        self.include_timestamp = include_timestamp
        self.auto_log_on_exit = auto_log_on_exit

        self._lines: List[Dict[str, str]] = []
        self._encountered_error = False
        self._start_time = datetime.now()

    def set_header_context(self, **kwargs) -> None:
        self.header_context.update(kwargs)

    def add(self, message: object, level: str = "INFO") -> None:
        lvl = (level or "INFO").upper()
        if lvl == "ERROR":
            self._encountered_error = True
        entry = {
            "level": lvl,
            "message": str(message),
        }
        if self.include_timestamp:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._lines.append(entry)

    def info(self, message: object) -> None:
        self.add(message, "INFO")

    def warning(self, message: object) -> None:
        self.add(message, "WARNING")

    def error(self, message: object) -> None:
        self.add(message, "ERROR")

    def step(self, message: object, details: Optional[Dict] = None) -> None:
        """Adds step message"""
        if details:
            message = f"{message} | {self.separator.join(f'{k}={v}' for k, v in details.items())}"
        self.add(message, "INFO")

    def _format_text(self) -> str:
        header_parts: List[str] = []
        if self.header:
            header_parts.append(self.header)
        if self.header_context:
            context_str = self.separator.join(f"{k}={v}" for k, v in self.header_context.items())
            if context_str:
                header_parts.append(context_str)
        header_text = self.separator.join(header_parts)

        detail_parts: List[str] = []
        for entry in self._lines:
            prefix = ""
            if self.include_timestamp and "timestamp" in entry:
                prefix += f"{entry['timestamp']} "
            if self.include_level:
                prefix += f"{entry['level']}: "
            detail_parts.append(prefix + entry["message"])

        details = self.separator.join(detail_parts)
        if header_text:
            return f"[{header_text}] {details}" if details else f"[{header_text}]"
        return details

    def log(self) -> None:
        text = self._format_text()
        if not text:
            return
        
        # Dosyaya kaydet
        self._save_to_file(text)
        
        # Also print to console
        if self._encountered_error:
            print(f"ERROR: {text}")
        else:
            print(f"INFO: {text}")

    def _save_to_file(self, text: str) -> None:
        """Saves log to file"""
        try:
            # Determine log directory
            log_dir = getattr(settings, 'LOG_HUB_LOG_DIR', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # Use the logger_name provided by the user
            safe_name = self.logger_name.replace('.', '_').replace('/', '_')
            filename = f"{safe_name}.log"
            filepath = os.path.join(log_dir, filename)
            
            # Log data
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR" if self._encountered_error else "INFO",
                "logger_name": self.logger_name,
                "header": self.header,
                "header_context": self.header_context,
                "message": text,
                "lines": self._lines,
                "duration_seconds": (datetime.now() - self._start_time).total_seconds()
            }
            
            # Append to file
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False, separators=(',', ':')) + '\n')
                
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def finish(self) -> None:
        """Completes the logging operation"""
        if self.auto_log_on_exit:
            self.log()


# Global logger instance
_global_aggregated_logger = None


def get_aggregated_logger(logger_name: Optional[str] = None) -> AggregatedLogger:
    """Returns global aggregated logger instance"""
    global _global_aggregated_logger
    if _global_aggregated_logger is None:
        _global_aggregated_logger = AggregatedLogger(logger_name=logger_name)
    return _global_aggregated_logger


def reset_aggregated_logger() -> None:
    """Resets global logger"""
    global _global_aggregated_logger
    _global_aggregated_logger = None


def log_step(message: str, details: Optional[Dict] = None) -> None:
    """Logs step message"""
    logger = get_aggregated_logger()
    logger.step(message, details)


def log_info(message: str) -> None:
    """Logs info message"""
    logger = get_aggregated_logger()
    logger.info(message)


def log_warning(message: str) -> None:
    """Logs warning message"""
    logger = get_aggregated_logger()
    logger.warning(message)


def log_error(message: str) -> None:
    """Logs error message"""
    logger = get_aggregated_logger()
    logger.error(message)


def finish_logging() -> None:
    """Completes the logging operation"""
    global _global_aggregated_logger
    if _global_aggregated_logger:
        _global_aggregated_logger.finish()
        _global_aggregated_logger = None


def aggregated_log(header: Optional[str] = None, logger_name: Optional[str] = None):
    """Aggregated logging decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Reset global logger
            reset_aggregated_logger()
            
            # Initialize logger
            actual_logger_name = logger_name
            if not actual_logger_name:
                actual_logger_name = func.__module__
            
            actual_header = header or func.__name__
            
            # Determine header context
            header_context = {}
            
            # Get user information if request object exists
            user_found = False
            
            # First, try to find request in args
            for arg in args:
                if hasattr(arg, 'user'):
                    if arg.user.is_authenticated:
                        header_context["user"] = getattr(arg.user, 'username', str(arg.user.id))
                    elif arg.user:
                        header_context["user"] = getattr(arg.user, 'username', str(arg.user.id))
                    else:
                        header_context["user"] = 'anonymous'
                    user_found = True
                    break
            
            # If not found in args, try to get from self.context (for serializers)
            if not user_found and len(args) > 0 and hasattr(args[0], 'context'):
                context = args[0].context
                if context and 'request' in context:
                    request = context['request']
                    if hasattr(request, 'user'):
                        if request.user.is_authenticated:
                            header_context["user"] = getattr(request.user, 'username', str(request.user.id))
                        elif request.user:
                            header_context["user"] = getattr(request.user, 'username', str(request.user.id))
                        else:
                            header_context["user"] = 'anonymous'
                        user_found = True
            
            # If still not found, set as anonymous
            if not user_found:
                header_context["user"] = 'anonymous'
            
            # Set global logger
            global _global_aggregated_logger
            _global_aggregated_logger = AggregatedLogger(
                logger_name=actual_logger_name,
                header=actual_header,
                header_context=header_context
            )
            
            try:
                # Entry log
                _global_aggregated_logger.info("Operation started")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Exit log
                _global_aggregated_logger.info("Operation completed")
                
                return result
                
            except Exception as e:
                # Error log
                _global_aggregated_logger.error(f"Operation error: {str(e)}")
                raise
            finally:
                # Complete logging operation
                finish_logging()
                
        return wrapper
    return decorator


# Simplified compatibility for old systems
class DynamicLogger:
    """Compatibility class for context manager usage"""
    
    def __init__(self, operation_name=None, user_id=None, logger_name=None):
        reset_aggregated_logger()
        self.logger = get_aggregated_logger(logger_name)
        self.logger.header = operation_name
        if user_id:
            self.logger.header_context["user"] = user_id
    
    def step(self, message, details=None):
        self.logger.step(message, details)
    
    def warning(self, message, details=None):
        self.logger.warning(message)
    
    def error(self, message, details=None):
        self.logger.error(message)
    
    def finish(self, save_logs=True):
        if save_logs:
            self.logger.finish()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.error(f"Error occurred during operation: {exc_val}")
        self.finish()


# Aliases for old system compatibility
def dynamic_log(operation_name=None, user_id=None, logger_name=None):
    """Compatibility for old system"""
    return aggregated_log(header=operation_name, logger_name=logger_name)


def centralized_log(operation_name=None, logger_name=None):
    """Compatibility for old system"""
    return aggregated_log(header=operation_name, logger_name=logger_name)


# Old names for backward compatibility
OperationLogger = DynamicLogger
log_operation = centralized_log


class LoggingMiddleware:
    """Middleware that automatically logs all requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get user information more reliably
        user_id = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = getattr(request.user, 'username', str(request.user.id))
        elif hasattr(request, 'user') and request.user:
            user_id = getattr(request.user, 'username', str(request.user.id))
        
        with DynamicLogger(
            operation_name=f"{request.method} {request.path}",
            user_id=user_id,
            logger_name="application"  # All logs go to the same file
        ) as logger:
            
            logger.step("Request received", {"method": request.method, "path": request.path, "user": user_id})
            
            response = self.get_response(request)
            
            logger.step("Response prepared", {"status_code": response.status_code})
            
            if response.status_code >= 400:
                logger.error(f"HTTP {response.status_code} error")
            
            return response

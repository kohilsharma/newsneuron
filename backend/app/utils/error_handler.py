"""
Enhanced error handling utilities for NewsNeuron backend
"""
import logging
import traceback
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import sys

logger = logging.getLogger(__name__)


class NewsNeuronError(Exception):
    """Base exception class for NewsNeuron"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(NewsNeuronError):
    """Validation error"""
    
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details or {}
        )
        if field:
            self.details["field"] = field


class DatabaseError(NewsNeuronError):
    """Database operation error"""
    
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details or {}
        )
        if operation:
            self.details["operation"] = operation


class ExternalServiceError(NewsNeuronError):
    """External service error (OpenAI, etc.)"""
    
    def __init__(self, message: str, service: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=503,
            details=details or {}
        )
        if service:
            self.details["service"] = service


class AuthenticationError(NewsNeuronError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationError(NewsNeuronError):
    """Authorization error"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403
        )


class RateLimitError(NewsNeuronError):
    """Rate limit error"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429
        )


def handle_database_error(error: Exception, operation: str = "database operation") -> NewsNeuronError:
    """Convert database errors to NewsNeuronError"""
    error_msg = str(error)
    
    # Handle specific database errors
    if "connection" in error_msg.lower():
        return DatabaseError(
            f"Database connection failed during {operation}",
            operation=operation,
            details={"original_error": error_msg}
        )
    elif "timeout" in error_msg.lower():
        return DatabaseError(
            f"Database operation timed out during {operation}",
            operation=operation,
            details={"original_error": error_msg}
        )
    elif "constraint" in error_msg.lower():
        return ValidationError(
            f"Data constraint violation during {operation}",
            details={"operation": operation, "original_error": error_msg}
        )
    else:
        return DatabaseError(
            f"Database error during {operation}: {error_msg}",
            operation=operation,
            details={"original_error": error_msg}
        )


def handle_external_service_error(error: Exception, service: str) -> ExternalServiceError:
    """Convert external service errors to NewsNeuronError"""
    error_msg = str(error)
    
    # Handle specific service errors
    if hasattr(error, 'response') and error.response:
        status = getattr(error.response, 'status_code', None)
        if status == 401:
            return ExternalServiceError(
                f"{service} authentication failed",
                service=service,
                details={"status_code": status, "original_error": error_msg}
            )
        elif status == 429:
            return RateLimitError(f"{service} rate limit exceeded")
        elif status >= 500:
            return ExternalServiceError(
                f"{service} service unavailable",
                service=service,
                details={"status_code": status, "original_error": error_msg}
            )
    
    return ExternalServiceError(
        f"{service} error: {error_msg}",
        service=service,
        details={"original_error": error_msg}
    )


async def newseuron_exception_handler(request: Request, exc: NewsNeuronError) -> JSONResponse:
    """Handle NewsNeuronError exceptions"""
    
    # Log the error
    logger.error(
        f"NewsNeuron error: {exc.error_code}",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
            "url": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    
    # Get error details
    error_details = {
        "type": type(exc).__name__,
        "url": str(request.url),
        "method": request.method
    }
    
    # Add stack trace in debug mode
    if logger.level <= logging.DEBUG:
        error_details["traceback"] = traceback.format_exc()
    
    # Log the error
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "error": str(exc),
            "details": error_details
        },
        exc_info=True
    )
    
    # Return appropriate response
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "error_code": "HTTP_EXCEPTION"
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            }
        )


def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {str(e)}", exc_info=True)
        raise NewsNeuronError(f"Error in {func.__name__}: {str(e)}")


async def async_safe_execute(func, *args, **kwargs):
    """Safely execute an async function with error handling"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {str(e)}", exc_info=True)
        raise NewsNeuronError(f"Error in {func.__name__}: {str(e)}")


def validate_required_fields(data: dict, required_fields: list, prefix: str = "") -> None:
    """Validate that required fields are present and not empty"""
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        field_name = f"{prefix}.{field}" if prefix else field
        
        if field not in data:
            missing_fields.append(field_name)
        elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field_name)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )
    
    if empty_fields:
        raise ValidationError(
            f"Empty required fields: {', '.join(empty_fields)}",
            details={"empty_fields": empty_fields}
        )


def validate_field_length(data: dict, field: str, max_length: int, min_length: int = 0) -> None:
    """Validate field length"""
    if field in data and data[field]:
        value = str(data[field])
        if len(value) < min_length:
            raise ValidationError(
                f"Field '{field}' must be at least {min_length} characters long",
                field=field
            )
        if len(value) > max_length:
            raise ValidationError(
                f"Field '{field}' must be no more than {max_length} characters long",
                field=field
            )


def validate_field_type(data: dict, field: str, expected_type: type) -> None:
    """Validate field type"""
    if field in data and data[field] is not None:
        if not isinstance(data[field], expected_type):
            raise ValidationError(
                f"Field '{field}' must be of type {expected_type.__name__}",
                field=field
            )


class ErrorContext:
    """Context manager for handling errors in specific operations"""
    
    def __init__(self, operation: str, service: str = None):
        self.operation = operation
        self.service = service
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False
        
        # Handle different types of exceptions
        if exc_type == NewsNeuronError:
            # Re-raise NewsNeuronError as-is
            return False
        elif "psycopg2" in str(exc_type) or "sqlalchemy" in str(exc_type):
            # Database error
            raise handle_database_error(exc_val, self.operation)
        elif self.service and ("openai" in str(exc_type).lower() or "http" in str(exc_type).lower()):
            # External service error
            raise handle_external_service_error(exc_val, self.service)
        else:
            # General error
            raise NewsNeuronError(
                f"Error in {self.operation}: {str(exc_val)}",
                details={"operation": self.operation, "original_error": str(exc_val)}
            )
        
        return False

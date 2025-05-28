"""Custom exceptions for Orion Vision Core."""

from typing import Any, Dict, Optional


class OrionError(Exception):
    """Base exception for all Orion Vision Core errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize OrionError.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class AgentError(OrionError):
    """Exception raised by agent operations."""
    
    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize AgentError.
        
        Args:
            message: Human-readable error message
            agent_name: Name of the agent that caused the error
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)
        self.agent_name = agent_name
        if agent_name:
            self.details["agent_name"] = agent_name


class ConfigError(OrionError):
    """Exception raised by configuration issues."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize ConfigError.
        
        Args:
            message: Human-readable error message
            config_key: Configuration key that caused the error
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class LLMError(OrionError):
    """Exception raised by LLM operations."""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize LLMError.
        
        Args:
            message: Human-readable error message
            model_name: Name of the LLM model that caused the error
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)
        self.model_name = model_name
        if model_name:
            self.details["model_name"] = model_name


class ValidationError(OrionError):
    """Exception raised by validation failures."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize ValidationError.
        
        Args:
            message: Human-readable error message
            field_name: Name of the field that failed validation
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)
        self.field_name = field_name
        if field_name:
            self.details["field_name"] = field_name


class TimeoutError(OrionError):
    """Exception raised when operations timeout."""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize TimeoutError.
        
        Args:
            message: Human-readable error message
            timeout_seconds: Timeout duration in seconds
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            self.details["timeout_seconds"] = timeout_seconds

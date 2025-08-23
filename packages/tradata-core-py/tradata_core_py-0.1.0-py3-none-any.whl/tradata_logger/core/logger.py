"""
Net-new logger interface - completely fresh design with operation and step tracking
"""
from typing import Any, Dict, Optional
from .engine import ModernLoggingEngine

class ModernLogger:
    """Net-new logger with trace ID, operation, and step tracking as first-class citizens"""
    
    def __init__(self, name: str, engine: ModernLoggingEngine):
        self.name = name
        self.engine = engine
    
    async def info(self, message: str, operation: str, step: str, **kwargs):
        """Info logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log("INFO", message, operation, step, logger=self.name, **kwargs)
    
    async def debug(self, message: str, operation: str, step: str, **kwargs):
        """Debug logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log("DEBUG", message, operation, step, logger=self.name, **kwargs)
    
    async def warning(self, message: str, operation: str, step: str, **kwargs):
        """Warning logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log("WARNING", message, operation, step, logger=self.name, **kwargs)
    
    async def error(self, message: str, operation: str, step: str, **kwargs):
        """Error logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log("ERROR", message, operation, step, logger=self.name, **kwargs)
    
    async def critical(self, message: str, operation: str, step: str, **kwargs):
        """Critical logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log("CRITICAL", message, operation, step, logger=self.name, **kwargs)
    
    def with_context(self, **context):
        """Add context to all subsequent log calls"""
        return ContextualLogger(self, context)
    
    def track_client(self, client_name: str):
        """Track which client is being used for this operation"""
        self.engine.client_used.set(client_name)
        return self
    
    async def log_cache_operation(self, step: str, cache_hit: bool, cache_key: str, duration_ms: float = None, **kwargs):
        """Log cache operations with structured key/value pairs"""
        extra = {
            "cacheHit": cache_hit,
            "cacheKey": cache_key,
            **kwargs
        }
        if duration_ms:
            extra["duration_ms"] = duration_ms
        
        # Remove any conflicting keys that match method parameters
        if "operation" in extra:
            del extra["operation"]
        if "step" in extra:
            del extra["step"]
        
        return await self.info("Cache operation", "Cache", step, **extra)
    
    async def log_client_operation(self, step: str, client_name: str, operation_name: str, duration_ms: float = None, **kwargs):
        """Log client operations with structured key/value pairs"""
        extra = {
            "client": client_name,
            "operation_name": operation_name,
            **kwargs
        }
        if duration_ms:
            extra["duration_ms"] = duration_ms
        
        # Remove any conflicting keys that match method parameters
        if "operation" in extra:
            del extra["operation"]
        if "step" in extra:
            del extra["step"]
        
        return await self.info(f"Client operation: {operation_name}", "Client", step, **extra)
    
    async def log_data_processing(self, step: str, **kwargs):
        """Log data processing operations"""
        return await self.info("Data processing operation", "DataProcessing", step, **kwargs)
    
    async def log_business_logic(self, step: str, **kwargs):
        """Log business logic operations"""
        return await self.info("Business logic operation", "BusinessLogic", step, **kwargs)
    
    async def log_error_handling(self, step: str, **kwargs):
        """Log error handling operations"""
        return await self.info("Error handling operation", "ErrorHandling", step, **kwargs)
    
    async def log_performance(self, step: str, **kwargs):
        """Log performance operations"""
        return await self.info("Performance operation", "Performance", step, **kwargs)
    
    async def log_mathematics(self, step: str, mathematical_principle: str = None, **kwargs):
        """Log mathematics operations with mathematical principle tracking"""
        extra = {
            "mathematical_principle": mathematical_principle,
            **kwargs
        }
        return await self.info("Mathematics operation", "Mathematics", step, **extra)

class ContextualLogger:
    """Logger with additional context"""
    
    def __init__(self, logger: ModernLogger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
    
    async def info(self, message: str, operation: str, step: str, **kwargs):
        """Info with context"""
        await self.logger.info(message, operation, step, **{**self.context, **kwargs})
    
    async def debug(self, message: str, operation: str, step: str, **kwargs):
        """Debug with context"""
        await self.logger.debug(message, operation, step, **{**self.context, **kwargs})
    
    async def warning(self, message: str, operation: str, step: str, **kwargs):
        """Warning with context"""
        await self.logger.warning(message, operation, step, **{**self.context, **kwargs})
    
    async def error(self, message: str, operation: str, step: str, **kwargs):
        """Error with context"""
        await self.logger.error(message, operation, step, **{**self.context, **kwargs})
    
    async def critical(self, message: str, operation: str, step: str, **kwargs):
        """Critical with context"""
        await self.logger.critical(message, operation, step, **{**self.context, **kwargs})


# Global logging engine instance
_logging_engine: Optional[ModernLoggingEngine] = None

def set_logging_engine(engine: ModernLoggingEngine):
    """Set the global logging engine instance"""
    global _logging_engine
    _logging_engine = engine

def get_logging_engine() -> ModernLoggingEngine:
    """Get the global logging engine instance"""
    global _logging_engine
    if _logging_engine is None:
        _logging_engine = ModernLoggingEngine()
    return _logging_engine

def get_logger(name: str) -> ModernLogger:
    """Get a logger instance for the specified name"""
    engine = get_logging_engine()
    return ModernLogger(name, engine)

def setup_logging(config: Optional[Dict[str, Any]] = None):
    """Setup logging with optional configuration"""
    engine = get_logging_engine()
    if config:
        # Apply configuration to engine
        pass
    return engine

# Context setting functions
def set_trace_id(trace_id: str):
    """Set the trace ID for the current context"""
    engine = get_logging_engine()
    engine.trace_id.set(trace_id)

def set_request_id(request_id: str):
    """Set the request ID for the current context"""
    engine = get_logging_engine()
    engine.request_id.set(request_id)

def set_client(client_name: str):
    """Set the client being used for the current context"""
    engine = get_logging_engine()
    engine.client_used.set(client_name)

def get_call_summary() -> Dict[str, Any]:
    """Get the current call summary"""
    engine = get_logging_engine()
    return engine.get_call_summary()

# Convenience function for quick logging
async def log(level: str, message: str, operation: str, step: str, **kwargs):
    """Quick logging function for simple use cases"""
    engine = get_logging_engine()
    await engine.log(level, message, operation, step, **kwargs)

# Convenience function for quick logging without async
def log_sync(level: str, message: str, operation: str, step: str, **kwargs):
    """Synchronous logging function for simple use cases"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, schedule the log
            asyncio.create_task(log(level, message, operation, step, **kwargs))
        else:
            # If no loop is running, run it
            asyncio.run(log(level, message, operation, step, **kwargs))
    except RuntimeError:
        # No event loop, create a new one
        asyncio.run(log(level, message, operation, step, **kwargs))

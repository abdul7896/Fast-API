"""
Performance monitoring middleware for request timing
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request processing time
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add timing header to response
        response.headers["X-Response-Time"] = str(round(process_time * 1000, 2))  # in milliseconds
        
        # Log slow requests (those taking more than 1 second)
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.2f}s"
            )
        
        logger.debug(
            f"Request: {request.method} {request.url.path} "
            f"processed in {process_time:.2f}s"
        )
        
        return response
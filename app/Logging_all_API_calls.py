from starlette.middleware.base import BaseHTTPMiddleware
import logging
from fastapi import Request

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.info(f"Request: {request.method} {request.url} {request.headers}")
        response = await call_next(request)
        logging.info(f"Response: {response.status_code} {response.headers}")
        return response
    
# app.add_middleware(LoggingMiddleware)
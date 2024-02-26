from fastapi import FastAPI, Request, HTTPException
from async_timeout import timeout
import time
import asyncio
import logging

class TimeoutMiddleware:
    def __init__(self, app: FastAPI, timeout_seconds: int = 3):
        self.app = app
        self.timeout_seconds = timeout_seconds

    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        try:
            async with timeout(self.timeout_seconds):
                response = await call_next(request)
            return response
        except asyncio.TimeoutError:
            logging.warning(
                f"TimeoutMiddleware: Request timed out after {time.time() - start_time} seconds.",
                extra={"path": request.url.path},
            )
            raise HTTPException(status_code=408, detail="Request timeout")

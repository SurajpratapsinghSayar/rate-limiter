from typing import Callable
from fastapi import FastAPI, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, Response
import time
from collections import deque


class SlidingWindowCounterLimiter(BaseHTTPMiddleware):
    """
    Middleware for throttling requests using sliding window counter algorithm.
    """

    def __init__(self, app: FastAPI, window_size: int = 60, threshold: int = 60):
        super().__init__(app)
        self.window_size = window_size
        self.max_requests = threshold
        self.request_timestamp = deque()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Intercept the incoming requests, check if requests are within the threshold and dispatch the request.

        Args:
            request (Request): incoming request
            call_next (Callable): next route

        Returns:
            Response: client response
        """
        self.cleanup_expired_requests()

        if len(self.request_timestamp) < self.max_requests:
            self.request_timestamp.append(time.time())
            return await call_next(request)
        else:
            try:
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"message": "Too many requests"},
                )
            except Exception as e:
                response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": f"Error handling request: {str(e)}"},
                )
            return response

    def cleanup_expired_requests(self):
        """
        Remove expired requests from the sliding window.
        """
        current_time = time.time()
        while (
            self.request_timestamp
            and current_time - self.request_timestamp[0] > self.window_size
        ):
            self.request_timestamp.popleft()


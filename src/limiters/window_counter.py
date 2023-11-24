from typing import Callable
from fastapi import FastAPI, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, Response
import multiprocessing
import time


def windowReset(requestCount, windowTime, threshold):
    while True:
        requestCount.value = threshold
        time.sleep(windowTime)


class WindowCounterLimiter(BaseHTTPMiddleware):
    """
    Middleware for throttling user access based on threshold counter and window size of N seconds.
    """

    def __init__(self, app: FastAPI, window_size: int = 60, threshold: int = 60):
        super().__init__(app)
        self.window_size = window_size
        self.threshold = threshold
        manager = multiprocessing.Manager()
        self.requestCount = multiprocessing.Value("i", threshold)
        process = multiprocessing.Process(
            target=windowReset,
            args=(self.requestCount, self.window_size, self.threshold),
        )
        process.start()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Intercept the incoming requests, check if requests are within the threshold and dispatch the request.

        Args:
            request (Request): incoming request
            call_next (Callable): next route

        Returns:
            Response: client response
        """
        if self.requestCount.value > 0:
            self.requestCount.value -= 1
            response = await call_next(request)
            return response
        else:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": "Too many requests"},
            )
            return response

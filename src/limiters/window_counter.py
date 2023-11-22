from typing import Callable
from fastapi import FastAPI, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, Response
import multiprocessing
import time


def windowReset(requestCount):
    while True:
        # Hardcoded to 60 requests per windowTime
        requestCount.value = 60
        # Hardcoded window timeframe to 60 seconds
        time.sleep(60)


class WindowCounterLimiter(BaseHTTPMiddleware):
    """
    Middleware for throttling user access based on threshold counter and window size of N seconds.
    """

    def __init__(self, app: FastAPI):
        super().__init__(app)
        manager = multiprocessing.Manager()
        self.requestCount = multiprocessing.Value("i", 60)
        process = multiprocessing.Process(
            target=windowReset,
            args=(self.requestCount,),
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

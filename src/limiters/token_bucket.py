from typing import Callable
from fastapi import FastAPI, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, Response
import multiprocessing
import time


def updateToken(ipBucket, bucketSize):
    while True:
        for ip in ipBucket.keys():
            if ipBucket[ip] < bucketSize:
                ipBucket[ip] += 1
        time.sleep(1)


def checkTokenAvailability(ip, ipBucket, bucketSize) -> bool:
    if ip not in ipBucket.keys():
        ipBucket[ip] = bucketSize
    if ipBucket[ip] > 0:
        ipBucket[ip] -= 1
        return True
    else:
        return False


class TokenBucketLimiter(BaseHTTPMiddleware):
    """
    Middleware for throttling user access based on tokens.
    """

    def __init__(self, app: FastAPI, bucketSize: int = 10):
        super().__init__(app)
        self.bucketSize = bucketSize
        manager = multiprocessing.Manager()
        self.ipBucket = manager.dict()
        process = multiprocessing.Process(target=updateToken, args=(self.ipBucket, self.bucketSize))
        process.start()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Intercept the incoming requests, check token availability and dispatch the request.

        Args:
            request (Request): incoming request
            call_next (Callable): next route

        Returns:
            Response: client response
        """
        flag = checkTokenAvailability(request.client.host, self.ipBucket, self.bucketSize)
        if flag:
            response = await call_next(request)
            return response
        else:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": "Too many requests"},
            )
            return response

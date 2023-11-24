from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from .limiters import TokenBucketLimiter
from .limiters import WindowCounterLimiter
from .limiters import SlidingWindowCounterLimiter
from datetime import datetime
import logging
import os


# logging ip addresses
log_folder = "src/logs"
os.makedirs(log_folder, exist_ok=True)
log_file_path = os.path.join(
    log_folder, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
)
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
)

app = FastAPI()


# --- Middleware ---

# app.add_middleware(TokenBucketLimiter, bucketSize = 10)
app.add_middleware(WindowCounterLimiter, window_size=60, threshold=100)
# app.add_middleware(SlidingWindowCounterLimiter, window_size=60, threshold=100)



@app.middleware("http")
def log_requests(request: Request, call_next):
    print(f"Request: {request.client.host}")
    logging.info(f"Logged IP: {request.client.host}")
    return call_next(request)


# --- Routes ---


@app.get("/")
def readRoot(request: Request):
    client_ip = request.client.host
    return {"message": "Hello, World!", "client_ip": client_ip}


@app.get("/unlimited")
def unLimited():
    return {"Unlimited! Let's Go!"}


@app.get("/limited")
def limited():
    return {"Limited, don't over use me!"}

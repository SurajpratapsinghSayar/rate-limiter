from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_root():
    headers = {"X-Forwarded-For": "127.0.0.1"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!", "client_ip": "testclient"}

def test_unlimited():
    response = client.get("/unlimited")
    assert response.status_code == 200
    assert response.json() == ["Unlimited! Let's Go!"]

def test_limited():
    response = client.get("/limited")
    assert response.status_code == 200
    assert response.json() == ["Limited, don't over use me!"]
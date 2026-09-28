import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test():
    res = client.get("/api/news?category=World&limit=2")
    print(res.json())

test()

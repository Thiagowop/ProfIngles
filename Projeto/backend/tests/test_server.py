#!/usr/bin/env python3
"""
Simple test to verify the server can start
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Server is running"}

if __name__ == "__main__":
    print("🚀 Starting simple test server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)

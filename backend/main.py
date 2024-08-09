# backend/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.analysis import router as analysis_router

app = FastAPI(title="Writer Analysis Tool")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Writer Analysis Tool API"}
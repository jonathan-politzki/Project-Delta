# backend/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.analysis import router as analysis_router
import nltk
nltk.data.path.append('./nltk_data')
import uvicorn

app = FastAPI(title="Writer Analysis Tool")

CORS_ORIGINS = [
    "https://*.vercel.app",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Writer Analysis Tool API"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

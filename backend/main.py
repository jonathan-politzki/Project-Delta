# backend/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.analysis import router as analysis_router
import os
import nltk
nltk.data.path.append('/app/nltk_data')


print("CORS_ORIGINS:", os.getenv("CORS_ORIGINS"))
print("API_URL:", os.getenv("API_URL"))

app = FastAPI()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://project-delta-lake.vercel.app").split(",")
CORS_ORIGINS.append("https://project-delta-g07nkry68-jonathan-politzkis-projects.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Writer Analysis Tool API"}

# creating an endpoint so we dont expose any environment variables to the frontend
@app.get("/api/config")
async def get_config():
    return {
        "apiUrl": os.getenv("API_URL", "http://localhost:8000")
    }

@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Received request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)



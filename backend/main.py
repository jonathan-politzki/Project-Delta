import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.analysis import router as analysis_router
import nltk
nltk.data.path.append('./nltk_data')
import uvicorn
import logging
from fastapi import Request


logger = logging.getLogger(__name__)

app = FastAPI(title="Writer Analysis Tool")

# Use environment variable for CORS_ORIGINS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://*.vercel.app,http://localhost:3000").split(",")

logger.info(f"CORS_ORIGINS: {CORS_ORIGINS}")

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

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Returning response: {response.status_code}")
    return response

@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    logger.info(f"Handling OPTIONS request for path: /{full_path}")
    logger.info(f"Request headers: {request.headers}")
    return {}



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
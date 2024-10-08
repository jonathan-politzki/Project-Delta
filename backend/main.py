import os
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.analysis import router as analysis_router
import nltk
nltk.data.path.append('./nltk_data')
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Writer Analysis Tool")

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Writer Analysis Tool API"}

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response

@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    logger.info(f"Handling OPTIONS request for path: /{full_path}")
    logger.info(f"Request headers: {request.headers}")
    return {}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
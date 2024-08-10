# backend/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.analysis import router as analysis_router

app = FastAPI(title="Writer Analysis Tool")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://project-delta-lake.vercel.app").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/", response_model=dict)
async def analyze_url(request: AnalysisRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(analyze_url_background, request.url, task_id)
    return {"task_id": task_id, "status": "processing"}

async def analyze_url_background(url: str, task_id: str):
    # Implement your analysis logic here
    # Store the result in a database or cache with the task_id as the key
    pass

@router.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    # Retrieve the status or result from the database or cache
    # Return the appropriate response
    pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
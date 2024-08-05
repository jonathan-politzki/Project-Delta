from fastapi import HTTPException

def handle_analysis_error(error: Exception) -> HTTPException:
    if isinstance(error, ValueError):
        return HTTPException(status_code=400, detail=str(error))
    elif isinstance(error, ConnectionError):
        return HTTPException(status_code=503, detail="Unable to connect to required services")
    else:
        return HTTPException(status_code=500, detail="An unexpected error occurred")

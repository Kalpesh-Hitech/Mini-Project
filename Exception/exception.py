from starlette.responses import JSONResponse
from starlette.requests import Request
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,status
 
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=400, content={"error": "Kuchh naya la"})
 
 
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Kuchh to gadbad h"})

async def credentials_exception(request: Request, exc: Exception):
    return JSONResponse(HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    ))
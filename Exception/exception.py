from starlette.responses import JSONResponse
from starlette.requests import Request
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=400, content={"error": "please change the data"})


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=400, content={"error": "please validate request data"}
    )


async def response_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=400, content={"error": "please validate reponse data"}
    )


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Kuchh to gadbad h"})


async def credentials_exception(request: Request, exc: Exception):
    return JSONResponse(
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    )

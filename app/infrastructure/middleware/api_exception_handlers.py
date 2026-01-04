from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.api_exception import ApiException


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom exception handlers for the provided FastAPI application.
    """

    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException):
        
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": str(exc.app_code.value), "message": str(exc.message)},
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        
        return JSONResponse(
            status_code=400,
            content={"code": "400", "message": str(exc)},
            headers={"Content-Type": "application/json"},
        )


from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import health_router, preparations_router
from backend.app.config import settings
from backend.app.exceptions import (
    InvalidPreparationInputError,
    PreparationDependencyError,
    PreparationNotFoundError,
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(preparations_router, prefix=settings.api_prefix)


@app.exception_handler(PreparationNotFoundError)
def handle_not_found(
    _request: Request,
    exc: PreparationNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidPreparationInputError)
def handle_invalid_input(
    _request: Request,
    exc: InvalidPreparationInputError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(exc)},
    )


@app.exception_handler(PreparationDependencyError)
def handle_dependency_error(
    _request: Request,
    exc: PreparationDependencyError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc)},
    )

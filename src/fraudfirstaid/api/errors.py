"""Standard API error responses using RFC 9457 Problem Details."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def problem_response(
    status: int,
    title: str,
    detail: str,
    instance: str,
    request_id: str | None = None,
    errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    """Build a standard Problem Details response."""

    content: dict[str, object] = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }

    if request_id:
        content["request_id"] = request_id

    if errors is not None:
        content["errors"] = errors

    return JSONResponse(
        status_code=status,
        content=content,
        media_type="application/problem+json",
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Convert HTTP exceptions into Problem Details."""

    return problem_response(
        status=exc.status_code,
        title=HTTPStatus(exc.status_code).phrase,
        detail=str(exc.detail),
        instance=request.url.path,
        request_id=getattr(request.state, "request_id", None),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Convert request validation errors into Problem Details."""

    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]

    return problem_response(
        status=422,
        title="Unprocessable Entity",
        detail="The request contains invalid or missing fields.",
        instance=request.url.path,
        request_id=getattr(request.state, "request_id", None),
        errors=errors,
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register RFC 9457 handlers for HTTP and validation errors."""

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

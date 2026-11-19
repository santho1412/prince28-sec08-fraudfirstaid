"""Standard API error responses using RFC 9457 Problem Details."""

from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def problem_response(
    status: int,
    title: str,
    detail: str,
    instance: str,
    request_id: str | None = None,
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

"""Request ID, timing, and exception handling middleware."""

import logging
import time
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestMiddleware(BaseHTTPMiddleware):
    """Add request IDs, measure duration, and handle unexpected errors."""

    async def dispatch(self, request: Request, call_next):
        request_id = uuid4().hex
        request.state.request_id = request_id
        start_time = time.perf_counter()

        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code

        except Exception:
            logger.exception(
                "request failed",
                extra={"request_id": request_id},
            )
            response = JSONResponse(
                status_code=500,
                media_type="application/problem+json",
                content={
                    "type": "about:blank",
                    "title": "Internal Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred.",
                    "instance": request.url.path,
                    "request_id": request_id,
                },
            )

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )

        return response

"""Request tracking, timing, and error logging middleware."""

import logging
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


class RequestContextMiddleware:
    """Attach a request ID and measure request duration."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        supplied_request_id = headers.get(b"x-request-id")

        request_id = (
            supplied_request_id.decode("latin-1") if supplied_request_id else uuid.uuid4().hex
        )

        scope.setdefault("state", {})["request_id"] = request_id
        start_time = time.perf_counter()

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                response_headers["X-Request-ID"] = request_id
                response_headers["X-Process-Time"] = f"{time.perf_counter() - start_time:.6f}"

            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        finally:
            logger.info(
                "request completed",
                extra={
                    "request_id": request_id,
                    "duration_seconds": round(
                        time.perf_counter() - start_time,
                        6,
                    ),
                },
            )

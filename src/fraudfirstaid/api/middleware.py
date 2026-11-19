"""Request tracking, timing, and error logging middleware."""

import logging
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


class RequestContextMiddleware:
    """Attach a unique request ID and measure request duration."""

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

        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        start_time = time.perf_counter()

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id
                headers["X-Process-Time"] = f"{time.perf_counter() - start_time:.6f}"

            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        except Exception:
            logger.exception(
                "unhandled request error",
                extra={"request_id": request_id},
            )
            raise
        finally:
            logger.info(
                "request completed",
                extra={
                    "request_id": request_id,
                    "duration_seconds": round(time.perf_counter() - start_time, 6),
                },
            )

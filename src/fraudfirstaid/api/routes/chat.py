"""POST /v1/chat (streaming) and GET /v1/usage (what the model calls cost)."""

import json
from collections.abc import AsyncIterator
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from fraudfirstaid.api.deps import GatewayDep, UsageDep
from fraudfirstaid.llm.gateway import LLMResult, LLMUnavailable

router = APIRouter(tags=["chat"])
PROMPT_VERSION = "chat_system_v1"


def load_prompt(directory: Path, name: str = PROMPT_VERSION) -> str:
    return (directory / f"{name}.md").read_text(encoding="utf-8").strip()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    stream: bool = True


def sse(data: dict, event: str = "") -> str:
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {json.dumps(data, ensure_ascii=False)}\n\n"


def summary(result: LLMResult) -> dict:
    return {key: value for key, value in asdict(result).items() if key != "text"}


@router.post("/chat")
async def chat(body: ChatRequest, request: Request, gateway: GatewayDep):
    messages = [
        {"role": "system", "content": request.app.state.system_prompt},
        {"role": "user", "content": body.message},
    ]

    if not body.stream:
        try:
            result = await gateway.generate(messages, prompt_version=PROMPT_VERSION)
        except LLMUnavailable as exc:
            raise HTTPException(status_code=503, detail=f"No model could answer: {exc}") from exc
        return {"answer": result.text, **summary(result)}

    stream = gateway.stream(messages, prompt_version=PROMPT_VERSION)

    try:
        first = await anext(stream)
    except LLMUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"No model could answer: {exc}") from exc

    async def events() -> AsyncIterator[str]:
        try:
            item = first
            while True:
                if isinstance(item, str):
                    yield sse({"delta": item})
                elif isinstance(item, LLMResult):
                    yield sse(summary(item), event="done")
                    return

                try:
                    item = await anext(stream)
                except StopAsyncIteration:
                    return
        except LLMUnavailable as exc:
            yield sse({"detail": str(exc)}, event="error")

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/usage")
async def usage(
    repo: UsageDep,
    days: Annotated[int, Query(ge=1, le=90)] = 7,
) -> dict:
    rows = await repo.by_day(days)
    total_cost = round(sum(row["cost_inr"] for row in rows), 4)
    return {
        "days": rows,
        "total_cost_inr": total_cost,
        "calls": sum(row["calls"] for row in rows),
    }

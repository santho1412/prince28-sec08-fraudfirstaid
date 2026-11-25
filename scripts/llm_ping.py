"""Send a direct ping to Gemini and Groq using their OpenAI-compatible APIs."""

import time

import httpx

from fraudfirstaid.config import get_settings


def ping_provider(
    name: str,
    api_key: str,
    base_url: str,
    model: str,
    timeout: float,
) -> bool:
    """Send one HTTP request and report the provider's response."""
    if not api_key:
        print(f"{name:<7} FAILED   API key is not configured")
        return False

    url = f"{base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly one word: pong"}],
        "max_tokens": 256,
        "temperature": 0,
    }

    start = time.perf_counter()

    try:
        response = httpx.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        response.raise_for_status()

        result = response.json()
        elapsed_ms = round((time.perf_counter() - start) * 1000)

        message = result["choices"][0]["message"]["content"]
        usage = result.get("usage") or {}

        prompt_tokens = usage.get("prompt_tokens", "?")
        completion_tokens = usage.get("completion_tokens", "?")

        print(
            f"{name:<7} OK       {model} said "
            f"{message!r} in {elapsed_ms} ms, "
            f"tokens in={prompt_tokens} out={completion_tokens}"
        )
        return True

    except httpx.HTTPStatusError as exc:
        print(f"{name:<7} FAILED   HTTP {exc.response.status_code}: {exc.response.text[:500]}")
    except httpx.TimeoutException:
        print(f"{name:<7} FAILED   Request timed out")
    except httpx.RequestError as exc:
        print(f"{name:<7} FAILED   Connection error: {exc}")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"{name:<7} FAILED   Unexpected response: {exc}")

    return False


def main() -> int:
    settings = get_settings()

    results = [
        ping_provider(
            "gemini",
            settings.gemini_api_key,
            settings.llm_primary_base_url,
            settings.llm_primary_model,
            settings.llm_timeout_seconds,
        ),
        ping_provider(
            "groq",
            settings.groq_api_key,
            settings.llm_fallback_base_url,
            settings.llm_fallback_model,
            settings.llm_timeout_seconds,
        ),
    ]

    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

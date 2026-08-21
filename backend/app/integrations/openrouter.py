import json
import os

import requests
from dotenv import load_dotenv


load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")
TIMEOUT = 90
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class LLMResponseError(RuntimeError):
    pass


def _parse_json_content(content: object) -> dict:
    if isinstance(content, dict):
        return content
    if not isinstance(content, str) or not content.strip():
        raise LLMResponseError("A LLM retornou uma resposta vazia.")

    value = content.strip()
    if value.startswith("```"):
        lines = value.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        value = "\n".join(lines).strip()

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise LLMResponseError("A LLM não retornou um JSON válido.") from exc

    if not isinstance(parsed, dict):
        raise LLMResponseError("A resposta estruturada da LLM deve ser um objeto JSON.")
    return parsed


def request_json(
    messages: list[dict[str, str]],
    schema: dict,
    schema_name: str,
    temperature: float = 0,
) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Defina OPENROUTER_API_KEY para usar a IA.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": messages,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "schema": schema,
                "strict": True,
            },
        },
        "temperature": temperature,
        "provider": {"require_parameters": True},
    }

    for attempt in range(2):
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=body,
                timeout=TIMEOUT,
            )
        except requests.ConnectionError:
            if attempt == 1:
                raise
            continue
        if response.status_code not in RETRYABLE_STATUS_CODES or attempt == 1:
            break
        response.close()
    response.raise_for_status()

    try:
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise LLMResponseError("Formato de resposta inesperado do provedor de LLM.") from exc

    return _parse_json_content(content)

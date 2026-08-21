import json
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_TIMEOUT = 30
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class GupyJobError(RuntimeError):
    pass


def clean_html(html: str | None) -> str:
    if not html:
        return ""
    text = BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
    return text.replace("\ufeff", "").strip()


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Informe uma URL HTTP(S) válida para a vaga.")


def fetch_gupy_job(url: str, timeout: float = DEFAULT_TIMEOUT) -> dict:
    _validate_url(url)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
        )
    }
    for attempt in range(2):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
        except requests.ConnectionError:
            if attempt == 1:
                raise
            continue
        if response.status_code not in RETRYABLE_STATUS_CODES or attempt == 1:
            break
        response.close()
    response.raise_for_status()

    script = BeautifulSoup(response.text, "html.parser").find(
        "script", id="__NEXT_DATA__"
    )
    if script is None or not script.string:
        raise GupyJobError("A página não contém os dados estruturados da vaga.")

    try:
        page_data = json.loads(script.string)
        job = page_data["props"]["pageProps"]["job"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise GupyJobError("A estrutura da página da vaga não é reconhecida.") from exc

    if not isinstance(job, dict):
        raise GupyJobError("Os dados encontrados para a vaga são inválidos.")
    return job

def clean_job_data(job: dict) -> dict:
    cleaned = {
        "titulo": clean_html(job.get("name")),
        "pre_requisitos": clean_html(job.get("prerequisites")),
        "responsabilidades": clean_html(job.get("responsibilities")),
    }
    if not cleaned["titulo"]:
        raise GupyJobError("A vaga não possui um título identificável.")
    return cleaned


def get_job(url: str) -> dict:
    return clean_job_data(fetch_gupy_job(url))

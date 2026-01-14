"""LLM 평가 도구 모음 패키지."""

from importlib import metadata as _metadata


def get_version() -> str:
    """패키지 버전을 반환."""
    try:
        return _metadata.version("iiac-lawlib-streamlit")
    except _metadata.PackageNotFoundError:  # pragma: no cover
        return "0.0.0"

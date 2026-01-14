"""평가 데이터셋 로딩 유틸리티."""

from pathlib import Path
from typing import List

DATASET_DIR = Path(__file__).resolve().parent


def list_datasets() -> List[str]:
    """데이터셋 파일 목록을 반환."""
    return sorted(
        p.name for p in DATASET_DIR.glob("*.json") if p.name != "template.json"
    )

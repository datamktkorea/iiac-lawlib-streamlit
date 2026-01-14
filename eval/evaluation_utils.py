"""평가를 위한 공통 유틸리티 함수."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def load_dataset(dataset_path: str | Path) -> List[Dict[str, Any]]:
    """평가 데이터셋을 로드합니다.

    Args:
        dataset_path: 데이터셋 JSON 파일 경로

    Returns:
        List[Dict[str, Any]]: 데이터셋 항목 리스트

    Raises:
        FileNotFoundError: 데이터셋 파일이 존재하지 않을 때
        json.JSONDecodeError: JSON 파싱 오류
    """
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"데이터셋 파일을 찾을 수 없습니다: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"데이터셋은 리스트 형식이어야 합니다: {dataset_path}")

    logger.info(f"데이터셋 로드 완료: {len(data)}개 항목 ({dataset_path})")
    return data


def save_results(results: Dict[str, Any], output_path: str | Path) -> None:
    """평가 결과를 JSON 파일로 저장합니다.

    Args:
        results: 평가 결과 딕셔너리
        output_path: 출력 파일 경로
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"평가 결과 저장 완료: {output_path}")


def validate_dataset_item(item: Dict[str, Any]) -> bool:
    """데이터셋 항목의 유효성을 검증합니다.

    Args:
        item: 데이터셋 항목

    Returns:
        bool: 유효성 여부
    """
    required_fields = ["id", "question", "expected_answer"]
    return all(field in item for field in required_fields)


def filter_dataset(
    dataset: List[Dict[str, Any]],
    max_samples: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """데이터셋을 필터링합니다.

    Args:
        dataset: 데이터셋 리스트
        max_samples: 최대 샘플 수 (None이면 제한 없음)
        tags: 필터링할 태그 리스트

    Returns:
        List[Dict[str, Any]]: 필터링된 데이터셋
    """
    filtered = dataset

    # 태그 필터링
    if tags:
        filtered = [
            item
            for item in filtered
            if any(tag in item.get("evaluation_tags", []) for tag in tags)
        ]

    # 샘플 수 제한
    if max_samples:
        filtered = filtered[:max_samples]

    return filtered


def calculate_aggregate_metrics(metrics_list: List[Dict[str, float]]) -> Dict[str, float]:
    """메트릭 리스트의 집계 값을 계산합니다.

    Args:
        metrics_list: 메트릭 딕셔너리 리스트

    Returns:
        Dict[str, float]: 집계된 메트릭 (평균값)
    """
    if not metrics_list:
        return {}

    aggregate = {}
    for key in metrics_list[0].keys():
        values = [m.get(key, 0.0) for m in metrics_list if key in m]
        if values:
            aggregate[key] = sum(values) / len(values)

    return aggregate


def format_duration(seconds: float) -> str:
    """초 단위 시간을 포맷팅합니다.

    Args:
        seconds: 초 단위 시간

    Returns:
        str: 포맷팅된 시간 문자열
    """
    if seconds < 60:
        return f"{seconds:.2f}초"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}분 {secs:.2f}초"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}시간 {minutes}분 {secs:.2f}초"




"""Langfuse 평가 실행 스크립트."""

import argparse
import json
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.config import RESULTS_DIR, config
from eval.evaluation_utils import save_results
from eval.langfuse_evaluator import run_evaluation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """메인 함수."""
    parser = argparse.ArgumentParser(description="Langfuse 평가 실행기")
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="평가 데이터셋 JSON 파일 경로",
    )
    parser.add_argument(
        "--llm-type",
        type=str,
        choices=["OpenAI", "Gemini"],
        default="OpenAI",
        help="사용할 LLM 타입 (기본값: OpenAI)",
    )
    parser.add_argument(
        "--model-version",
        type=str,
        default="gpt-4o-mini",
        help="사용할 모델 버전 (기본값: gpt-4o-mini)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="최대 평가 샘플 수 (기본값: 제한 없음)",
    )
    parser.add_argument(
        "--tags",
        type=str,
        nargs="+",
        default=None,
        help="필터링할 태그 리스트",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="결과 출력 파일 경로 (기본값: eval/results/langfuse_results.json)",
    )
    parser.add_argument(
        "--enable-llm-judge",
        action="store_true",
        default=True,
        help="LLM-as-a-Judge 평가 활성화 (기본값: True)",
    )
    parser.add_argument(
        "--disable-llm-judge",
        action="store_false",
        dest="enable_llm_judge",
        help="LLM-as-a-Judge 평가 비활성화",
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        default="gpt-4o-mini",
        help="평가에 사용할 Judge 모델 (기본값: gpt-4o-mini)",
    )

    args = parser.parse_args()

    # 환경 변수 검증
    missing = config.validate_required_env()
    if missing:
        logger.error(f"필수 환경 변수가 누락되었습니다: {', '.join(missing)}")
        sys.exit(1)

    # Langfuse 설정 확인
    if not config.is_langfuse_enabled():
        logger.warning(
            "Langfuse가 활성화되지 않았습니다. "
            "LANGFUSE_PUBLIC_KEY와 LANGFUSE_SECRET_KEY를 설정해주세요."
        )
        logger.info(f"현재 LANGFUSE_HOST: {config.langfuse_host}")

    # 데이터셋 경로 확인
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        logger.error(f"데이터셋 파일을 찾을 수 없습니다: {dataset_path}")
        sys.exit(1)

    # 평가 실행
    logger.info("Langfuse 평가 시작...")
    results = run_evaluation(
        dataset_path=dataset_path,
        llm_type=args.llm_type,
        model_version=args.model_version,
        max_samples=args.max_samples,
        tags=args.tags,
        enable_llm_judge=args.enable_llm_judge,
        judge_model=args.judge_model,
    )

    # 결과 저장
    output_path = args.output or RESULTS_DIR / "langfuse_results.json"
    save_results(results, output_path)

    # 결과 요약 출력
    print("\n" + "=" * 80)
    print("Langfuse 평가 결과 요약")
    print("=" * 80)
    print(f"평가 샘플 수: {results.get('evaluated_samples', 0)}")
    print(f"소요 시간: {results.get('elapsed_time_formatted', 'N/A')}")
    metrics = results.get("aggregate_metrics", {})
    if metrics:
        print("메트릭:")
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)):
                print(f"  {metric_name}: {metric_value:.4f}")
    print(f"\n결과 파일: {output_path}")
    print(f"Langfuse 대시보드: {config.langfuse_host}")
    print("=" * 80)


if __name__ == "__main__":
    main()

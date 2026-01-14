"""Phoenix LLM 테스트 실행 스크립트."""

import argparse
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.ai_phoenix_evaluator import (
    launch_phoenix_app,
    setup_phoenix_tracing,
    test_llm_with_phoenix,
    test_rag_chain_with_phoenix,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """메인 함수."""
    parser = argparse.ArgumentParser(description="Phoenix LLM 테스트 실행기")
    parser.add_argument(
        "--test-type",
        type=str,
        choices=["llm", "rag"],
        default="llm",
        help="테스트 타입: 'llm' (단순 LLM) 또는 'rag' (RAG 체인) (기본값: llm)",
    )
    parser.add_argument(
        "--question",
        type=str,
        default="인천국제공항공사는 무엇인가요?",
        help="테스트할 질문 (기본값: '인천국제공항공사는 무엇인가요?')",
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
        "--port",
        type=int,
        default=6006,
        help="Phoenix 서버 포트 (기본값: 6006)",
    )
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Phoenix UI를 자동으로 시작하지 않음",
    )
    parser.add_argument(
        "--project-name",
        type=str,
        default="iiac-lawlib",
        help="Phoenix 프로젝트 이름 (기본값: iiac-lawlib)",
    )

    args = parser.parse_args()

    # Phoenix 추적 설정
    logger.info("Phoenix 추적 설정 중...")
    if not setup_phoenix_tracing(project_name=args.project_name):
        logger.error("Phoenix 추적 설정 실패")
        sys.exit(1)

    # Phoenix UI 시작 (선택적)
    session = None
    phoenix_url = None
    if not args.no_ui:
        session = launch_phoenix_app(port=args.port)
        if session:
            phoenix_url = f"http://localhost:{args.port}"

    # 테스트 실행
    logger.info(f"테스트 시작: {args.test_type}")
    logger.info(f"질문: {args.question}")
    logger.info(f"모델: {args.llm_type}/{args.model_version}")

    if args.test_type == "llm":
        result = test_llm_with_phoenix(
            question=args.question,
            llm_type=args.llm_type,
            model_version=args.model_version,
            launch_ui=False,  # 이미 시작했으므로 False
            port=args.port,
        )
    else:  # rag
        result = test_rag_chain_with_phoenix(
            question=args.question,
            llm_type=args.llm_type,
            model_version=args.model_version,
            launch_ui=False,  # 이미 시작했으므로 False
            port=args.port,
        )

    # 결과 출력
    logger.info("\n" + "=" * 80)
    logger.info("테스트 결과")
    logger.info("=" * 80)

    if result["success"]:
        logger.info("✅ 테스트 성공!")
        logger.info(f"질문: {result['question']}")
        logger.info(f"답변: {result['answer'][:500]}...")  # 처음 500자만 출력

        if args.test_type == "rag" and result.get("source_documents"):
            logger.info(f"참조 문서 수: {len(result['source_documents'])}")

        if phoenix_url:
            logger.info(f"\n📊 Phoenix UI: {phoenix_url}")
            logger.info("   위 URL에서 추적 결과를 확인할 수 있습니다.")
    else:
        logger.error(f"❌ 테스트 실패: {result.get('error')}")
        sys.exit(1)

    logger.info("=" * 80)


if __name__ == "__main__":
    main()

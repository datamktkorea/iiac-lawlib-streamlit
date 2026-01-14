"""lm-evaluation-harness를 사용한 LangChain 평가 실행 스크립트."""

import argparse
import json
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from eval.config import config
from eval.lm_eval_harness_evaluator import (
    LangChainModel,
    evaluate_with_lm_eval,
    test_langchain_chain,
)

load_dotenv(".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """메인 함수."""
    parser = argparse.ArgumentParser(description="LangChain 체인 테스트 실행기")
    parser.add_argument(
        "--question",
        type=str,
        help="테스트할 질문 (단일 질문)",
    )
    parser.add_argument(
        "--questions-file",
        type=str,
        help=(
            "질문 리스트가 담긴 JSON 파일 경로 "
            "(각 항목은 'question' 키를 가져야 함)"
        ),
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
        "--output",
        type=str,
        help="결과 출력 파일 경로 (JSON 형식, 선택사항)",
    )
    parser.add_argument(
        "--task",
        type=str,
        help=(
            "lm-evaluation-harness 태스크 이름 (예: hellaswag, mmlu, iiac_mcq). "
            "이 옵션을 사용하면 실제 평가를 실행합니다."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="평가할 샘플 수 제한 (기본값: 제한 없음)",
    )

    args = parser.parse_args()

    # 환경 변수 검증
    missing = config.validate_required_env()
    if missing:
        logger.error(f"필수 환경 변수가 누락되었습니다: {', '.join(missing)}")
        sys.exit(1)

    # lm-evaluation-harness 평가 모드
    if args.task:
        logger.info(f"lm-evaluation-harness 평가 모드: {args.task}")
        try:
            results = evaluate_with_lm_eval(
                task=args.task,
                llm_type=args.llm_type,
                model_version=args.model_version,
                limit=args.limit,
            )

            # 결과 출력
            print("\n" + "=" * 80)
            print(f"lm-evaluation-harness 평가 결과: {args.task}")
            print("=" * 80)
            print(json.dumps(results, ensure_ascii=False, indent=2))
            print("=" * 80)

            # 결과 저장
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                logger.info(f"결과 저장 완료: {output_path}")

            return

        except ImportError as e:
            logger.error(f"lm-evaluation-harness 평가 실패: {e}")
            sys.exit(1)

    # 질문 확인
    if not args.question and not args.questions_file:
        parser.error("--question, --questions-file, 또는 --task 중 하나는 필수입니다.")

    if args.question and args.questions_file:
        parser.error("--question과 --questions-file은 동시에 사용할 수 없습니다.")

    results = []

    # 단일 질문 테스트
    if args.question:
        logger.info(f"질문 테스트 시작: {args.question}")
        answer = test_langchain_chain(
            question=args.question,
            llm_type=args.llm_type,
            model_version=args.model_version,
        )

        result = {
            "question": args.question,
            "answer": answer,
            "llm_type": args.llm_type,
            "model_version": args.model_version,
        }
        results.append(result)

        # 결과 출력
        print("\n" + "=" * 80)
        print("LangChain 체인 테스트 결과")
        print("=" * 80)
        print(f"질문: {args.question}")
        print(f"답변: {answer}")
        print("=" * 80)

    # 여러 질문 테스트
    elif args.questions_file:
        questions_path = Path(args.questions_file)
        if not questions_path.exists():
            logger.error(f"질문 파일을 찾을 수 없습니다: {questions_path}")
            sys.exit(1)

        with open(questions_path, "r", encoding="utf-8") as f:
            questions_data = json.load(f)

        # 질문 리스트 추출
        if isinstance(questions_data, list):
            questions = [
                item.get("question", item) if isinstance(item, dict) else item
                for item in questions_data
            ]
        elif isinstance(questions_data, dict) and "questions" in questions_data:
            questions = questions_data["questions"]
        else:
            logger.error(
                "질문 파일 형식이 올바르지 않습니다. "
                "리스트 또는 {'questions': [...]} 형식이어야 합니다."
            )
            sys.exit(1)

        logger.info(f"{len(questions)}개 질문 테스트 시작...")

        model = LangChainModel(llm_type=args.llm_type, model_version=args.model_version)

        for idx, question in enumerate(questions, 1):
            logger.info(f"질문 {idx}/{len(questions)}: {question}")
            answer = model.generate(question)

            result = {
                "question": question,
                "answer": answer,
                "llm_type": args.llm_type,
                "model_version": args.model_version,
            }
            results.append(result)

            print(f"\n[{idx}/{len(questions)}] 질문: {question}")
            print(f"답변: {answer}")

        print("\n" + "=" * 80)
        print(f"총 {len(results)}개 질문 테스트 완료")
        print("=" * 80)

    # 결과 저장
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"결과 저장 완료: {output_path}")


if __name__ == "__main__":
    main()

"""Langfuse를 사용한 LLM 평가 실행기.

Langfuse의 Score API와 LLM-as-a-Judge 기능을 활용하여
RAG 체인의 성능을 평가하고 점수를 저장합니다.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from app.core.rag_chain import build_chain
from eval.evaluation_utils import (
    calculate_aggregate_metrics,
    filter_dataset,
    format_duration,
    load_dataset,
    validate_dataset_item,
)

logger = logging.getLogger(__name__)


class LangfuseEvaluator:
    """Langfuse를 사용한 평가 실행기.

    Langfuse의 Score API와 LLM-as-a-Judge를 활용하여
    RAG 체인의 성능을 평가하고 점수를 저장합니다.
    """

    def __init__(
        self,
        llm_type: str = "OpenAI",
        model_version: str = "gpt-4o-mini",
        enable_llm_judge: bool = True,
        judge_model: str = "gpt-4o-mini",
    ):
        """LangfuseEvaluator 인스턴스를 초기화합니다.

        Args:
            llm_type: 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
            model_version: 사용할 모델 버전.
            enable_llm_judge: LLM-as-a-Judge 평가 활성화 여부.
            judge_model: 평가에 사용할 Judge 모델 (기본값: gpt-4o-mini).
        """
        self.llm_type = llm_type
        self.model_version = model_version
        self.enable_llm_judge = enable_llm_judge
        self.judge_model = judge_model
        self.langfuse_handler = self._create_langfuse_handler()
        self.judge_llm = self._create_judge_llm() if enable_llm_judge else None

    def _create_langfuse_handler(self) -> CallbackHandler | None:
        """Langfuse 콜백 핸들러를 생성합니다.

        환경 변수에서 Langfuse 인증 정보를 읽어 콜백 핸들러를 생성합니다.
        환경 변수가 설정되지 않은 경우 None을 반환합니다.

        환경 변수:
            LANGFUSE_PUBLIC_KEY: Langfuse 공개 키
            LANGFUSE_SECRET_KEY: Langfuse 비밀 키
            LANGFUSE_HOST: Langfuse 호스트 URL (선택, 기본값: https://cloud.langfuse.com)

        Returns:
            CallbackHandler | None: Langfuse 콜백 핸들러 또는 None.
        """
        load_dotenv()
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")

        if not public_key or not secret_key:
            logger.warning("Langfuse 환경 변수가 설정되지 않았습니다. 추적 기능이 비활성화됩니다.")
            return None

        try:
            return CallbackHandler()
        except Exception as e:
            logger.warning(f"Langfuse 콜백 핸들러 생성 실패: {e}")
            return None

    def _create_judge_llm(self) -> ChatOpenAI | None:
        """LLM-as-a-Judge에 사용할 LLM을 생성합니다.

        Returns:
            ChatOpenAI | None: Judge LLM 또는 None.
        """
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY가 설정되지 않았습니다. LLM-as-a-Judge가 비활성화됩니다.")
            return None

        try:
            return ChatOpenAI(model=self.judge_model, temperature=0)
        except Exception as e:
            logger.warning(f"Judge LLM 생성 실패: {e}")
            return None

    def evaluate(
        self,
        dataset_path: str | Path,
        max_samples: int | None = None,
        tags: List[str] | None = None,
    ) -> Dict[str, Any]:
        """데이터셋을 평가합니다.

        Args:
            dataset_path: 평가 데이터셋 경로
            max_samples: 최대 샘플 수 (None이면 제한 없음)
            tags: 필터링할 태그 리스트

        Returns:
            Dict[str, Any]: 평가 결과
        """
        logger.info(f"Langfuse 평가 시작: {dataset_path}")

        # 데이터셋 로드
        dataset = load_dataset(dataset_path)
        dataset = filter_dataset(dataset, max_samples=max_samples, tags=tags)

        # 유효성 검증
        valid_dataset = [item for item in dataset if validate_dataset_item(item)]
        if len(valid_dataset) != len(dataset):
            logger.warning(f"일부 항목이 유효하지 않습니다: {len(dataset) - len(valid_dataset)}개")

        results = []
        start_time = time.time()

        # 각 항목 평가
        for idx, item in enumerate(valid_dataset, 1):
            logger.info(f"평가 중 ({idx}/{len(valid_dataset)}): {item['id']}")
            result = self._evaluate_item(item)
            results.append(result)

        elapsed_time = time.time() - start_time

        # 집계 메트릭 계산
        metrics_list = [r["metrics"] for r in results if "metrics" in r]
        aggregate_metrics = calculate_aggregate_metrics(metrics_list)

        evaluation_result = {
            "tool": "langfuse",
            "llm_type": self.llm_type,
            "model_version": self.model_version,
            "dataset_path": str(dataset_path),
            "total_samples": len(valid_dataset),
            "evaluated_samples": len(results),
            "elapsed_time": elapsed_time,
            "elapsed_time_formatted": format_duration(elapsed_time),
            "aggregate_metrics": aggregate_metrics,
            "results": results,
        }

        logger.info(
            f"Langfuse 평가 완료: {len(results)}개 샘플 평가 ({format_duration(elapsed_time)})"
        )

        return evaluation_result

    def _evaluate_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """단일 항목을 평가합니다.

        Args:
            item: 평가 항목

        Returns:
            Dict[str, Any]: 평가 결과
        """
        question = item["question"]
        expected_answer = item.get("expected_answer", "")

        # 메시지 히스토리 생성
        messages = ChatMessageHistory()

        # 체인 빌드
        chain = build_chain(self.llm_type, self.model_version, messages)

        # 질문 실행
        start_time = time.time()
        try:
            # LangChain 호출 설정
            config_dict = {"configurable": {"session_id": f"eval_{item['id']}"}}

            # Langfuse 콜백이 있으면 추가 (자동으로 trace 생성됨)
            if self.langfuse_handler:
                config_dict["callbacks"] = [self.langfuse_handler]

            result = chain.invoke({"question": question}, config=config_dict)

            elapsed_time = time.time() - start_time

            # 응답 추출
            answer = result.get("output", "") if isinstance(result, dict) else str(result)

            # 기본 메트릭 계산
            metrics = {
                "response_time": elapsed_time,
                "has_response": bool(answer),
                "response_length": len(answer) if answer else 0,
            }

            # LLM-as-a-Judge 평가 수행
            judge_scores = {}
            if self.enable_llm_judge and self.judge_llm and answer:
                judge_scores = self._run_llm_judge(
                    question=question,
                    answer=answer,
                    expected_answer=expected_answer,
                )
                metrics.update(judge_scores)

            evaluation_result = {
                "id": item["id"],
                "question": question,
                "expected_answer": expected_answer,
                "answer": answer,
                "metrics": metrics,
                "status": "success",
            }

            # source_documents가 있으면 추가
            if isinstance(result, dict) and "source_documents" in result:
                evaluation_result["source_documents"] = result["source_documents"]

            return evaluation_result

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"항목 평가 실패 ({item['id']}): {e}")

            return {
                "id": item["id"],
                "question": question,
                "expected_answer": expected_answer,
                "answer": "",
                "metrics": {
                    "response_time": elapsed_time,
                    "has_response": False,
                    "response_length": 0,
                },
                "status": "error",
                "error": str(e),
            }

    def _run_llm_judge(
        self,
        question: str,
        answer: str,
        expected_answer: str,
    ) -> Dict[str, float]:
        """LLM-as-a-Judge를 사용하여 답변을 평가합니다.

        Langfuse 문서를 참고하여 구현:
        https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge

        Args:
            question: 질문
            answer: 생성된 답변
            expected_answer: 기대 답변 (선택)

        Returns:
            Dict[str, float]: 평가 점수 딕셔너리
        """
        if not self.judge_llm:
            return {}

        scores = {}

        # Relevance 평가
        relevance_score = self._evaluate_relevance(question, answer)
        scores["relevance"] = relevance_score

        # Accuracy 평가 (expected_answer가 있는 경우)
        if expected_answer:
            accuracy_score = self._evaluate_accuracy(answer, expected_answer)
            scores["accuracy"] = accuracy_score

        # Helpfulness 평가
        helpfulness_score = self._evaluate_helpfulness(question, answer)
        scores["helpfulness"] = helpfulness_score

        return scores

    def _evaluate_relevance(self, question: str, answer: str) -> float:
        """답변의 관련성을 평가합니다.

        Args:
            question: 질문
            answer: 답변

        Returns:
            float: 관련성 점수 (0.0 ~ 1.0)
        """
        if not self.judge_llm:
            return 0.0

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert evaluator. Evaluate how relevant the answer is to the question. "
                    "Return a JSON object with 'score' (0.0-1.0) and 'reasoning' (string).",
                ),
                (
                    "human",
                    "Question: {question}\n\nAnswer: {answer}\n\n"
                    "Evaluate the relevance of the answer to the question. "
                    "Score: 1.0 = highly relevant, 0.0 = not relevant at all.",
                ),
            ]
        )

        try:
            chain = prompt | self.judge_llm
            response = chain.invoke({"question": question, "answer": answer})
            result = json.loads(response.content)
            return float(result.get("score", 0.0))
        except Exception as e:
            logger.warning(f"Relevance 평가 실패: {e}")
            return 0.0

    def _evaluate_accuracy(self, answer: str, expected_answer: str) -> float:
        """답변의 정확성을 평가합니다.

        Args:
            answer: 생성된 답변
            expected_answer: 기대 답변

        Returns:
            float: 정확성 점수 (0.0 ~ 1.0)
        """
        if not self.judge_llm:
            return 0.0

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert evaluator. Evaluate how accurate the answer is compared to the expected answer. "
                    "Return a JSON object with 'score' (0.0-1.0) and 'reasoning' (string).",
                ),
                (
                    "human",
                    "Expected Answer: {expected_answer}\n\nGenerated Answer: {answer}\n\n"
                    "Evaluate the accuracy of the generated answer. "
                    "Score: 1.0 = completely accurate, 0.0 = completely inaccurate.",
                ),
            ]
        )

        try:
            chain = prompt | self.judge_llm
            response = chain.invoke({"answer": answer, "expected_answer": expected_answer})
            result = json.loads(response.content)
            return float(result.get("score", 0.0))
        except Exception as e:
            logger.warning(f"Accuracy 평가 실패: {e}")
            return 0.0

    def _evaluate_helpfulness(self, question: str, answer: str) -> float:
        """답변의 유용성을 평가합니다.

        Args:
            question: 질문
            answer: 답변

        Returns:
            float: 유용성 점수 (0.0 ~ 1.0)
        """
        if not self.judge_llm:
            return 0.0

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert evaluator. Evaluate how helpful the answer is to the user. "
                    "Return a JSON object with 'score' (0.0-1.0) and 'reasoning' (string).",
                ),
                (
                    "human",
                    "Question: {question}\n\nAnswer: {answer}\n\n"
                    "Evaluate how helpful and informative the answer is. "
                    "Score: 1.0 = very helpful, 0.0 = not helpful at all.",
                ),
            ]
        )

        try:
            chain = prompt | self.judge_llm
            response = chain.invoke({"question": question, "answer": answer})
            result = json.loads(response.content)
            return float(result.get("score", 0.0))
        except Exception as e:
            logger.warning(f"Helpfulness 평가 실패: {e}")
            return 0.0


def run_evaluation(
    dataset_path: str | Path,
    llm_type: str = "OpenAI",
    model_version: str = "gpt-4o-mini",
    max_samples: int | None = None,
    tags: List[str] | None = None,
    enable_llm_judge: bool = True,
    judge_model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """Langfuse 평가를 실행합니다.

    Args:
        dataset_path: 평가 데이터셋 경로
        llm_type: 사용할 LLM 타입
        model_version: 사용할 모델 버전
        max_samples: 최대 샘플 수
        tags: 필터링할 태그 리스트
        enable_llm_judge: LLM-as-a-Judge 평가 활성화 여부
        judge_model: 평가에 사용할 Judge 모델

    Returns:
        Dict[str, Any]: 평가 결과
    """
    evaluator = LangfuseEvaluator(
        llm_type=llm_type,
        model_version=model_version,
        enable_llm_judge=enable_llm_judge,
        judge_model=judge_model,
    )
    return evaluator.evaluate(
        dataset_path=dataset_path,
        max_samples=max_samples,
        tags=tags,
    )

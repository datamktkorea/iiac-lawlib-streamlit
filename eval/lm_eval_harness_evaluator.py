"""lm-evaluation-harness를 사용한 LangChain 평가 실행기.

LangChain 체인을 lm-evaluation-harness와 통합하여 평가합니다.
"""

import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple

from langchain_community.chat_message_histories import ChatMessageHistory

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.rag_chain import build_chain

logger = logging.getLogger(__name__)


# lm-eval import (선택적)
# eval/datasets 디렉토리가 datasets 패키지와 충돌하지 않도록 처리
def _import_lm_eval():
    """lm_eval을 import하는 헬퍼 함수.

    eval/datasets 디렉토리가 datasets 패키지 import를
    방해하지 않도록 처리합니다.
    """
    # sys.modules에서 잘못된 datasets import 제거
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith("eval.datasets")]
    for module in modules_to_remove:
        del sys.modules[module]

    with _temporary_remove_eval_dir():
        try:
            from lm_eval.api.instance import Instance
            from lm_eval.api.model import LM

            return True, LM, Instance
        except ImportError:
            return False, None, None


class _temporary_remove_eval_dir:
    """eval 디렉토리를 sys.path에서 잠시 제거하는 컨텍스트 매니저."""

    def __init__(self) -> None:
        """컨텍스트 매니저를 초기화합니다."""
        self.eval_dir = str(Path(__file__).parent.resolve())
        self.removed_paths: List[str] = []

    def __enter__(self) -> "_temporary_remove_eval_dir":
        """컨텍스트 진입 시 eval 디렉토리를 제거합니다."""
        for path in list(sys.path):
            if path == self.eval_dir:
                sys.path.remove(path)
                self.removed_paths.append(path)
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        """컨텍스트 종료 시 eval 디렉토리를 복원합니다."""
        if self.removed_paths:
            sys.path[:0] = self.removed_paths
        return None


class _safe_path_relative_to:
    """Path.relative_to 메서드를 안전하게 패치하는 컨텍스트 매니저.

    lm_eval 라이브러리의 pretty_print_task 함수에서 커스텀 태스크 경로를
    처리할 때 발생하는 ValueError를 방지합니다.
    """

    def __init__(self) -> None:
        """원본 메서드를 저장합니다."""
        self._original_relative_to = Path.relative_to

    def __enter__(self) -> "_safe_path_relative_to":
        """Path.relative_to를 안전한 버전으로 패치합니다."""
        original = self._original_relative_to

        def safe_relative_to(self_path: Path, other: Path) -> Path:
            """상대 경로 계산 실패 시 원본 경로를 반환합니다."""
            try:
                return original(self_path, other)
            except ValueError:
                # 상대 경로 계산 실패 시 파일명만 반환
                return Path(self_path.name)

        Path.relative_to = safe_relative_to
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        """원본 메서드를 복원합니다."""
        Path.relative_to = self._original_relative_to
        return None


def _normalize_stop_sequences(until: Optional[object]) -> Optional[List[str]]:
    """중단 시퀀스 입력을 정규화합니다.

    Args:
        until: 중단 시퀀스 입력 값.

    Returns:
        Optional[List[str]]: 정규화된 중단 시퀀스 리스트.
    """
    if until is None:
        return None
    if isinstance(until, str):
        return [until]
    if isinstance(until, Sequence):
        normalized = [value for value in until if isinstance(value, str) and value]
        return normalized or None
    return None


def _truncate_at_stop_sequences(text: str, until: Optional[Sequence[str]]) -> str:
    """중단 시퀀스가 등장하는 지점에서 텍스트를 자릅니다.

    Args:
        text: 원본 텍스트.
        until: 중단 시퀀스 리스트.

    Returns:
        str: 중단 시퀀스를 제외한 텍스트.
    """
    if not until:
        return text

    earliest_index = None
    for sequence in until:
        index = text.find(sequence)
        if index != -1 and (earliest_index is None or index < earliest_index):
            earliest_index = index

    return text[:earliest_index] if earliest_index is not None else text


def _normalize_choice_text(choice: str) -> str:
    """선택지 텍스트를 정규화합니다.

    Args:
        choice: 원본 선택지 텍스트.

    Returns:
        str: 정규화된 선택지 텍스트.
    """
    return choice.lstrip()


def _parse_choice_index(answer: str, choice_count: int) -> Optional[int]:
    """모델 응답에서 선택지 번호를 추출합니다.

    Args:
        answer: 모델 응답 텍스트.
        choice_count: 선택지 개수.

    Returns:
        Optional[int]: 0 기반 인덱스. 추출 실패 시 None.
    """
    if choice_count <= 0:
        return None

    match = re.search(r"\d+", answer)
    if not match:
        return None

    index = int(match.group(0)) - 1
    if 0 <= index < choice_count:
        return index
    return None


def _collect_tasks_with_names(task_dict: dict) -> List[Tuple[str, Any]]:
    """중첩된 태스크 딕셔너리에서 태스크 객체를 수집합니다.

    Args:
        task_dict: 태스크 딕셔너리.

    Returns:
        List[Tuple[str, Any]]: (태스크 이름, 태스크 객체) 목록.
    """
    collected: List[Tuple[str, Any]] = []
    for key, value in task_dict.items():
        if isinstance(value, dict):
            collected.extend(_collect_tasks_with_names(value))
            continue
        if isinstance(key, str):
            name = key
        else:
            task_name = getattr(getattr(value, "config", None), "task", None)
            task_alias = getattr(getattr(value, "config", None), "task_alias", None)
            name = task_name or task_alias or value.__class__.__name__
        collected.append((name, value))
    return collected


def _get_task_output_type(task: Any) -> Optional[str]:
    """태스크에서 출력 타입을 추출합니다.

    Args:
        task: lm-eval 태스크 객체.

    Returns:
        Optional[str]: 출력 타입.
    """
    config = getattr(task, "config", None)
    if config is not None and getattr(config, "output_type", None):
        return config.output_type
    return getattr(task, "OUTPUT_TYPE", None)


try:
    LM_EVAL_AVAILABLE, LM, Instance = _import_lm_eval()
    if not LM_EVAL_AVAILABLE:
        logger.warning("lm-eval이 설치되지 않았습니다. LM 기능을 사용할 수 없습니다.")
except Exception:
    LM_EVAL_AVAILABLE = False
    LM = None
    Instance = None
    logger.warning("lm-eval import 실패")


class LangChainModel:
    """LangChain 체인을 lm-evaluation-harness와 호환되도록 래핑하는 클래스.

    LangChain 체인을 호출하여 질문에 대한 답변을 생성합니다.
    """

    def __init__(self, llm_type: str = "OpenAI", model_version: str = "gpt-4o-mini"):
        """LangChainModel 인스턴스를 초기화합니다.

        Args:
            llm_type: 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
            model_version: 사용할 모델 버전.
        """
        self.llm_type = llm_type
        self.model_version = model_version

    def generate(self, prompt: str, gen_kwargs: Optional[dict] = None) -> str:
        """프롬프트에 대한 답변을 생성합니다.

        Args:
            prompt: 입력 프롬프트 (질문).
            gen_kwargs: 생성 옵션 (중단 시퀀스 등).

        Returns:
            str: 생성된 답변.
        """
        try:
            messages = ChatMessageHistory()
            chain = build_chain(self.llm_type, self.model_version, messages)
            config = {"configurable": {"session_id": "lm_eval_session"}}
            result = chain.invoke({"question": prompt}, config=config)

            # 응답 추출
            if isinstance(result, dict):
                answer = result.get("output", "")
            else:
                answer = str(result)

            until = _normalize_stop_sequences(gen_kwargs.get("until") if gen_kwargs else None)
            truncated = _truncate_at_stop_sequences(answer, until)
            return truncated if truncated else ""
        except Exception as e:
            logger.error(f"LangChain 체인 호출 실패: {e}")
            return ""

    def generate_requests(
        self,
        prompts: List[str],
        gen_kwargs_list: Optional[List[Optional[dict]]] = None,
    ) -> List[str]:
        """여러 프롬프트에 대한 답변을 생성합니다.

        Args:
            prompts: 입력 프롬프트 리스트.
            gen_kwargs_list: 프롬프트별 생성 옵션 리스트.

        Returns:
            List[str]: 생성된 답변 리스트.
        """
        if gen_kwargs_list is None:
            return [self.generate(prompt) for prompt in prompts]
        return [
            self.generate(prompt, gen_kwargs=gen_kwargs)
            for prompt, gen_kwargs in zip(prompts, gen_kwargs_list)
        ]

    def select_choice(self, context: str, choices: List[str]) -> int:
        """문맥과 보기에서 가장 적절한 선택지를 고릅니다.

        Args:
            context: 문제 문맥 또는 질문.
            choices: 선택지 리스트.

        Returns:
            int: 선택된 인덱스.
        """
        if not choices:
            return 0

        prompt_lines = [
            "다음 문맥에 가장 잘 맞는 선택지를 번호로만 답하세요.",
            "",
            f"문맥: {context}",
            "",
            "선택지:",
        ]
        for idx, choice in enumerate(choices, 1):
            prompt_lines.append(f"{idx}. {choice}")
        prompt = "\n".join(prompt_lines)

        answer = self.generate(prompt)
        parsed_index = _parse_choice_index(answer, len(choices))
        if parsed_index is not None:
            return parsed_index

        normalized_answer = answer.strip()
        for idx, choice in enumerate(choices):
            normalized_choice = choice.strip()
            if normalized_choice and normalized_choice in normalized_answer:
                return idx

        return 0


def test_langchain_chain(
    question: str,
    llm_type: str = "OpenAI",
    model_version: str = "gpt-4o-mini",
) -> str:
    """LangChain 체인을 간단히 테스트합니다.

    Args:
        question: 테스트할 질문.
        llm_type: 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
        model_version: 사용할 모델 버전.

    Returns:
        str: 생성된 답변.

    Examples:
        >>> answer = test_langchain_chain("인천국제공항공사는 무엇인가요?")
        >>> print(answer)
    """
    model = LangChainModel(llm_type=llm_type, model_version=model_version)
    return model.generate(question)


if LM_EVAL_AVAILABLE and LM is not None:

    class LangChainLM(LM):
        """LangChain 체인을 lm-evaluation-harness LM으로 래핑하는 클래스.

        LangChain RAG 체인을 lm-evaluation-harness와 통합하여 평가할 수 있도록
        합니다.
        """

        def __init__(
            self,
            llm_type: str = "OpenAI",
            model_version: str = "gpt-4o-mini",
            allow_multiple_choice: bool = True,
            **kwargs,
        ):
            """LangChainLM 인스턴스를 초기화합니다.

            Args:
                llm_type: 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
                model_version: 사용할 모델 버전.
                **kwargs: LM의 추가 인자.
            """
            super().__init__()
            self.llm_type = llm_type
            self.model_version = model_version
            self.allow_multiple_choice = allow_multiple_choice
            self._model = LangChainModel(llm_type=llm_type, model_version=model_version)

        def generate_until(self, requests: List[Instance]) -> List[str]:
            """여러 요청에 대한 답변을 생성합니다.

            Args:
                requests: Instance 객체 리스트. args는 (context, gen_kwargs) 튜플입니다.

            Returns:
                List[str]: 생성된 답변 리스트.
            """
            prompts = [req.args[0] for req in requests]
            gen_kwargs_list = []
            for req in requests:
                if len(req.args) > 1 and isinstance(req.args[1], dict):
                    gen_kwargs_list.append(req.args[1])
                else:
                    gen_kwargs_list.append(None)
            return self._model.generate_requests(prompts, gen_kwargs_list=gen_kwargs_list)

        def loglikelihood(self, requests: List[Instance]) -> List[Tuple[float, bool]]:
            """로그 우도 계산 (근사적 다중 선택 지원).

            Args:
                requests: Instance 객체 리스트.

            Returns:
                List[Tuple[float, bool]]: (로그 우도, is_greedy) 튜플 리스트.
            """
            if not requests:
                return []

            grouped_requests: dict[Tuple[Optional[str], Optional[int]], List[Instance]] = {}
            for req in requests:
                key = (req.task_name, req.doc_id)
                grouped_requests.setdefault(key, []).append(req)

            has_multiple_choice = any(len(group) > 1 for group in grouped_requests.values())
            if not has_multiple_choice or not self.allow_multiple_choice:
                raise NotImplementedError(
                    "LangChain RAG 체인에서는 loglikelihood를 계산할 수 없습니다."
                )

            logger.warning("multiple_choice 태스크는 근사적인 선택지 추론으로 평가됩니다.")

            results: List[Tuple[float, bool]] = []
            for group in grouped_requests.values():
                results.extend(self._score_multiple_choice_group(group))

            return results

        def _score_multiple_choice_group(
            self, requests: List[Instance]
        ) -> List[Tuple[float, bool]]:
            """다중 선택 요청 그룹을 점수화합니다.

            Args:
                requests: 동일 문항에 대한 Instance 리스트.

            Returns:
                List[Tuple[float, bool]]: 요청 순서에 맞춘 점수 리스트.
            """
            if not requests:
                return []

            conditional_requests: List[Instance] = []
            conditional_index_map: dict[int, int] = {}
            for req in requests:
                if len(req.args) > 0 and isinstance(req.args[0], str) and req.args[0]:
                    conditional_index_map[id(req)] = len(conditional_requests)
                    conditional_requests.append(req)

            if not conditional_requests:
                for req in requests:
                    conditional_index_map[id(req)] = len(conditional_requests)
                    conditional_requests.append(req)

            context = conditional_requests[0].args[0] if conditional_requests else ""
            choices = [
                _normalize_choice_text(req.args[1])
                if len(req.args) > 1 and isinstance(req.args[1], str)
                else ""
                for req in conditional_requests
            ]

            selected_index = self._model.select_choice(context, choices)

            scored: List[Tuple[float, bool]] = []
            for req in requests:
                idx = conditional_index_map.get(id(req))
                if idx is not None and choices:
                    is_selected = idx == selected_index
                    scored.append((1.0 if is_selected else 0.0, is_selected))
                else:
                    scored.append((0.0, False))
            return scored

        def loglikelihood_rolling(self, requests: List[Instance]) -> List[float]:
            """롤링 로그 우도 계산 (구현되지 않음).

            Args:
                requests: Instance 객체 리스트.

            Returns:
                List[float]: 로그 우도 리스트.
            """
            raise NotImplementedError(
                "LangChain RAG 체인에서는 loglikelihood_rolling을 계산할 수 없습니다."
            )

        @property
        def max_length(self) -> int:
            """최대 시퀀스 길이를 반환합니다.

            Returns:
                int: 최대 길이 (기본값: 2048).
            """
            return 2048

        @property
        def max_gen_toks(self) -> int:
            """최대 생성 토큰 수를 반환합니다.

            Returns:
                int: 최대 생성 토큰 수 (기본값: 512).
            """
            return 512

        @property
        def batch_size(self) -> int:
            """배치 크기를 반환합니다.

            Returns:
                int: 배치 크기 (기본값: 1).
            """
            return 1

        @property
        def device(self) -> str:
            """디바이스를 반환합니다.

            Returns:
                str: 디바이스 (기본값: "cpu").
            """
            return "cpu"


def evaluate_with_lm_eval(
    task: str = "hellaswag",
    llm_type: str = "OpenAI",
    model_version: str = "gpt-4o-mini",
    limit: int | None = None,
    allow_multiple_choice: bool = True,
) -> dict:
    """lm-evaluation-harness를 사용하여 LangChain 체인을 평가합니다.

    Args:
        task: 평가할 태스크 이름 (예: "hellaswag", "mmlu").
        llm_type: 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
        model_version: 사용할 모델 버전.
        limit: 평가할 샘플 수 제한 (None이면 제한 없음).
        allow_multiple_choice: 다중 선택 태스크의 근사 평가 허용 여부.

    Returns:
        dict: 평가 결과.

    Examples:
        >>> result = evaluate_with_lm_eval(
        ...     task="hellaswag",
        ...     llm_type="OpenAI",
        ...     model_version="gpt-4o-mini",
        ...     limit=10
        ... )
    """
    if not LM_EVAL_AVAILABLE:
        raise ImportError(
            "lm-eval이 설치되지 않았습니다. 다음 명령어로 설치하세요: uv add 'lm-eval[api]'"
        )

    # eval/datasets 디렉토리가 datasets 패키지와 충돌하지 않도록 처리
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith("eval.datasets")]
    for module in modules_to_remove:
        del sys.modules[module]

    try:
        with _temporary_remove_eval_dir():
            from lm_eval.evaluator import simple_evaluate
            from lm_eval.tasks import get_task_dict
            from lm_eval.tasks import TaskManager
    except ImportError as e:
        raise ImportError(f"lm_eval.simple_evaluate를 import할 수 없습니다: {e}")

    logger.info(f"LangChain 체인 평가 시작: {task} (모델: {llm_type}/{model_version})")

    # 프로젝트 루트로 작업 디렉토리 변경 (YAML 파일 내 상대 경로 해결)
    project_root = Path(__file__).parent.parent.resolve()
    original_cwd = os.getcwd()

    try:
        os.chdir(project_root)
        logger.debug(f"작업 디렉토리 변경: {original_cwd} -> {project_root}")

        task_include_path = Path(__file__).parent / "lm_eval_tasks"
        task_manager = TaskManager(include_path=[str(task_include_path)])

        # lm_eval의 pretty_print_task에서 커스텀 경로 처리 시 오류 방지
        with _safe_path_relative_to():
            task_dict = get_task_dict([task], task_manager=task_manager)
            tasks_with_names = _collect_tasks_with_names(task_dict)
            unsupported = []
            has_multiple_choice = False
            for task_name, task_obj in tasks_with_names:
                output_type = _get_task_output_type(task_obj)
                if output_type == "multiple_choice":
                    has_multiple_choice = True
                    continue
                if output_type != "generate_until":
                    unsupported.append(f"{task_name}({output_type})")
            if unsupported:
                raise ValueError(
                    "LangChain RAG 체인은 generate_until 출력 타입만 지원합니다. "
                    f"지원하지 않는 태스크: {', '.join(unsupported)}"
                )
            if has_multiple_choice and not allow_multiple_choice:
                raise ValueError(
                    "multiple_choice 태스크는 근사 평가만 지원합니다. "
                    "allow_multiple_choice=True로 실행하세요."
                )
            if has_multiple_choice:
                logger.warning("multiple_choice 태스크는 근사 평가로 실행됩니다.")

            # LangChain 모델 생성
            model = LangChainLM(
                llm_type=llm_type,
                model_version=model_version,
                allow_multiple_choice=allow_multiple_choice,
            )

            # 평가 실행
            results = simple_evaluate(
                model=model,
                tasks=[task],
                limit=limit,
                batch_size=1,
                task_manager=task_manager,
            )

            logger.info(f"평가 완료: {task}")
            return results
    finally:
        os.chdir(original_cwd)
        logger.debug(f"작업 디렉토리 복원: {original_cwd}")

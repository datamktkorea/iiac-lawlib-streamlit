"""Phoenix를 사용한 LLM 추적 및 평가 모듈.

Phoenix를 사용하여 LangChain 체인의 LLM 호출을 추적하고 평가합니다.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.chat_message_histories import ChatMessageHistory

from app.core.rag_chain import build_chain

logger = logging.getLogger(__name__)

# Phoenix 관련 import (선택적)
# 참고: https://arize.com/docs/phoenix/integrations/python/langchain/langchain-tracing
try:
    import phoenix as px
    from phoenix.otel import register

    PHOENIX_AVAILABLE = True
    _PHOENIX_TRACING_SETUP = False  # 중복 설정 방지
except ImportError as e:
    PHOENIX_AVAILABLE = False
    _PHOENIX_TRACING_SETUP = False
    logger.warning(f"Phoenix가 설치되지 않았습니다: {e}. Phoenix 기능을 사용할 수 없습니다.")


def launch_phoenix_app(port: int = 6006) -> Any | None:
    """Phoenix 웹 UI를 시작합니다.

    로컬에서 Phoenix 서버를 시작합니다. Docker를 사용하려면 별도로 설정하세요.
    참고: https://arize.com/docs/phoenix/self-hosting/deployment-options/docker

    Args:
        port: Phoenix 서버 포트 (기본값: 6006).
            - 6006: UI 및 OTLP HTTP collector
            - 4317: OTLP gRPC collector (필요시)

    Returns:
        Optional[Any]: Phoenix 세션 객체 또는 None (Phoenix가 설치되지 않은 경우).

    Examples:
        >>> session = launch_phoenix_app()
        >>> # Phoenix UI가 http://localhost:6006 에서 실행됩니다

    Note:
        - 포트가 이미 사용 중인 경우 Phoenix가 자동으로 다른 포트를 사용할 수 있습니다.
        - Docker를 사용하는 경우: `docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest`
        - 실제 사용된 포트는 반환된 세션 객체에서 확인할 수 있습니다.
    """
    if not PHOENIX_AVAILABLE:
        logger.error("Phoenix가 설치되지 않았습니다. 'uv add arize-phoenix'로 설치하세요.")
        return None

    try:
        logger.info(f"Phoenix 서버 시작 중... (포트: {port})")
        session = px.launch_app(port=port)
        logger.info(f"Phoenix UI가 http://localhost:{port} 에서 실행 중입니다.")
        logger.info("   (포트가 이미 사용 중이면 다른 포트가 자동으로 할당될 수 있습니다)")
        return session
    except OSError as e:
        if "Address already in use" in str(e) or "address already in use" in str(e).lower():
            logger.warning(
                f"포트 {port}가 이미 사용 중입니다. 다른 포트를 시도하거나 기존 Phoenix 인스턴스를 종료하세요."
            )
        logger.error(f"Phoenix 서버 시작 실패: {e}")
        return None
    except Exception as e:
        logger.error(f"Phoenix 서버 시작 실패: {e}")
        return None


def setup_phoenix_tracing(project_name: str = "iiac-lawlib") -> bool:
    """Phoenix 추적을 설정합니다.

    LangChain을 자동으로 추적하도록 설정합니다.
    공식 문서에 따라 `register()` 함수의 `auto_instrument=True` 옵션을 사용합니다.
    중복 설정을 방지하기 위해 이미 설정된 경우 재설정하지 않습니다.

    참고: https://arize.com/docs/phoenix/integrations/python/langchain/langchain-tracing

    Args:
        project_name: Phoenix 프로젝트 이름 (기본값: "iiac-lawlib").

    Returns:
        bool: 설정 성공 여부.

    Examples:
        >>> success = setup_phoenix_tracing("my-project")
        >>> if success:
        ...     print("Phoenix 추적이 활성화되었습니다.")
    """
    global _PHOENIX_TRACING_SETUP

    if not PHOENIX_AVAILABLE:
        logger.error("Phoenix가 설치되지 않았습니다.")
        return False

    # 이미 설정된 경우 재설정하지 않음
    if _PHOENIX_TRACING_SETUP:
        logger.debug("Phoenix 추적이 이미 설정되어 있습니다.")
        return True

    try:
        # Phoenix tracer provider 등록
        # 공식 문서에 따라 auto_instrument=True를 사용하면 자동으로 LangChain이 추적됨
        # 참고: https://arize.com/docs/phoenix/integrations/python/langchain/langchain-tracing
        register(project_name=project_name, auto_instrument=True)
        _PHOENIX_TRACING_SETUP = True
        logger.info(f"Phoenix 추적이 활성화되었습니다. (프로젝트: {project_name})")
        logger.info("LangChain이 자동으로 추적됩니다.")
        return True
    except Exception as e:
        logger.error(f"Phoenix 추적 설정 실패: {e}")
        return False


def test_llm_with_phoenix(
    question: str = "인천국제공항공사는 무엇인가요?",
    llm_type: str = "OpenAI",
    model_version: str = "gpt-4o-mini",
    launch_ui: bool = True,
    port: int = 6006,
) -> Dict[str, Any]:
    """Phoenix를 사용하여 LLM을 테스트하는 최소 단위 함수.

    Phoenix를 통해 LangChain 체인의 LLM 호출을 추적하고 결과를 반환합니다.

    Args:
        question: 테스트할 질문 (기본값: "인천국제공항공사는 무엇인가요?").
        llm_type: 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
        model_version: 사용할 모델 버전.
        launch_ui: Phoenix UI를 자동으로 시작할지 여부 (기본값: True).
        port: Phoenix 서버 포트 (기본값: 6006).

    Returns:
        Dict[str, Any]: 테스트 결과 딕셔너리.
            - success: 성공 여부
            - answer: 생성된 답변
            - phoenix_url: Phoenix UI URL (UI가 시작된 경우)
            - error: 오류 메시지 (실패한 경우)

    Examples:
        >>> result = test_llm_with_phoenix(
        ...     question="인천국제공항공사는 무엇인가요?",
        ...     llm_type="OpenAI",
        ...     model_version="gpt-4o-mini"
        ... )
        >>> print(result["answer"])
        >>> print(f"Phoenix UI: {result.get('phoenix_url')}")
    """
    if not PHOENIX_AVAILABLE:
        return {
            "success": False,
            "error": "Phoenix가 설치되지 않았습니다. 'uv add arize-phoenix'로 설치하세요.",
        }

    # Phoenix 추적 설정
    if not setup_phoenix_tracing():
        return {"success": False, "error": "Phoenix 추적 설정 실패"}

    # Phoenix UI 시작 (선택적)
    session = None
    phoenix_url = None
    if launch_ui:
        session = launch_phoenix_app(port=port)
        if session:
            phoenix_url = f"http://localhost:{port}"

    try:
        # RAG 체인 생성 및 실행
        logger.info(f"LLM 테스트 시작: {question}")
        messages = ChatMessageHistory()
        chain = build_chain(llm_type, model_version, messages)
        config = {"configurable": {"session_id": "phoenix_test_session"}}
        result = chain.invoke({"question": question}, config=config)

        # 응답 추출
        if isinstance(result, dict):
            answer = result.get("output", "")
        else:
            answer = str(result)

        logger.info("LLM 테스트 완료")

        return {
            "success": True,
            "answer": answer if answer else "",
            "phoenix_url": phoenix_url,
            "question": question,
            "llm_type": llm_type,
            "model_version": model_version,
        }
    except Exception as e:
        logger.error(f"LLM 테스트 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "phoenix_url": phoenix_url,
        }


def test_rag_chain_with_phoenix(
    question: str = "인천국제공항공사의 주요 업무는 무엇인가요?",
    llm_type: str = "OpenAI",
    model_version: str = "gpt-4o-mini",
    launch_ui: bool = True,
    port: int = 6006,
) -> Dict[str, Any]:
    """Phoenix를 사용하여 RAG 체인을 테스트합니다.

    RAG 체인의 전체 파이프라인(검색 + 생성)을 Phoenix로 추적합니다.

    Args:
        question: 테스트할 질문.
        llm_type: 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
        model_version: 사용할 모델 버전.
        launch_ui: Phoenix UI를 자동으로 시작할지 여부 (기본값: True).
        port: Phoenix 서버 포트 (기본값: 6006).

    Returns:
        Dict[str, Any]: 테스트 결과 딕셔너리.
            - success: 성공 여부
            - answer: 생성된 답변
            - source_documents: 참조된 문서 메타데이터
            - phoenix_url: Phoenix UI URL
            - error: 오류 메시지 (실패한 경우)

    Examples:
        >>> result = test_rag_chain_with_phoenix(
        ...     question="인천국제공항공사의 주요 업무는?",
        ...     llm_type="OpenAI"
        ... )
        >>> print(result["answer"])
        >>> print(f"참조 문서 수: {len(result.get('source_documents', []))}")
    """
    if not PHOENIX_AVAILABLE:
        return {
            "success": False,
            "error": "Phoenix가 설치되지 않았습니다. 'uv add arize-phoenix'로 설치하세요.",
        }

    # Phoenix 추적 설정
    if not setup_phoenix_tracing():
        return {"success": False, "error": "Phoenix 추적 설정 실패"}

    # Phoenix UI 시작 (선택적)
    session = None
    phoenix_url = None
    if launch_ui:
        session = launch_phoenix_app(port=port)
        if session:
            phoenix_url = f"http://localhost:{port}"

    try:
        # RAG 체인 생성 및 실행
        logger.info(f"RAG 체인 테스트 시작: {question}")
        messages = ChatMessageHistory()
        chain = build_chain(llm_type, model_version, messages)
        config = {"configurable": {"session_id": "phoenix_rag_test_session"}}
        result = chain.invoke({"question": question}, config=config)

        # 응답 및 메타데이터 추출
        if isinstance(result, dict):
            answer = result.get("output", "")
            source_documents = result.get("source_documents", [])
        else:
            answer = str(result)
            source_documents = []

        logger.info(f"RAG 체인 테스트 완료 (참조 문서 수: {len(source_documents)})")

        return {
            "success": True,
            "answer": answer if answer else "",
            "source_documents": source_documents,
            "phoenix_url": phoenix_url,
            "question": question,
            "llm_type": llm_type,
            "model_version": model_version,
        }
    except Exception as e:
        logger.error(f"RAG 체인 테스트 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "phoenix_url": phoenix_url,
        }


if __name__ == "__main__":
    """직접 실행 시 최소 단위 테스트를 수행합니다."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("=" * 80)
    logger.info("Phoenix LLM 테스트 시작")
    logger.info("=" * 80)

    # 최소 단위 LLM 테스트
    result = test_llm_with_phoenix(
        question="인천국제공항공사는 무엇인가요?",
        llm_type="OpenAI",
        model_version="gpt-4o-mini",
    )

    if result["success"]:
        logger.info("\n✅ 테스트 성공!")
        logger.info(f"질문: {result['question']}")
        logger.info(f"답변: {result['answer'][:200]}...")  # 처음 200자만 출력
        if result.get("phoenix_url"):
            logger.info(f"\n📊 Phoenix UI: {result['phoenix_url']}")
            logger.info("   위 URL에서 추적 결과를 확인할 수 있습니다.")
    else:
        logger.error(f"\n❌ 테스트 실패: {result.get('error')}")

    logger.info("=" * 80)

"""평가 설정 관리 모듈."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(".env")

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
EVAL_ROOT = Path(__file__).parent
DATASETS_DIR = EVAL_ROOT / "datasets"
RESULTS_DIR = EVAL_ROOT / "results"

# 결과 디렉토리 생성
RESULTS_DIR.mkdir(exist_ok=True)


class EvaluationConfig:
    """평가 설정을 관리하는 클래스."""

    def __init__(self):
        """EvaluationConfig 인스턴스를 초기화합니다."""
        # Langfuse 설정
        self.langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        # OpenAI/Gemini 설정
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

        # 기본 모델 설정
        self.default_llm_type = "OpenAI"
        self.default_model_version = "gpt-4o-mini"

        # RAG 설정
        self.chroma_db_path = PROJECT_ROOT / "chroma_langchain_db"
        self.chroma_collection_name = "iiac_poc"

        # 평가 설정
        self.max_eval_samples = None  # None이면 모든 샘플 평가
        self.timeout_seconds = 300  # 타임아웃 (초)

    def validate_required_env(self) -> list[str]:
        """필수 환경 변수를 검증하고 누락된 변수 목록을 반환합니다.

        Returns:
            list[str]: 누락된 환경 변수 목록
        """
        missing = []
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        return missing

    def is_langfuse_enabled(self) -> bool:
        """Langfuse가 활성화되어 있는지 확인합니다.

        Returns:
            bool: Langfuse 활성화 여부
        """
        return bool(self.langfuse_public_key and self.langfuse_secret_key)


# 전역 설정 인스턴스
config = EvaluationConfig()




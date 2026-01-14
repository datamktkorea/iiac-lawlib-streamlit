# AGENTS.md - AI 에이전트 가이드

이 문서는 `iiac-lawlib-streamlit` 프로젝트에서 AI 코딩 에이전트가 따라야 할 규칙과 가이드라인을 정의합니다.

## 1. 프로젝트 개요

인천국제공항공사(IIAC)의 법률 및 규정 정보를 검색하고 질의응답할 수 있는 AI 기반 챗봇 서비스입니다.
Streamlit 기반 웹 애플리케이션으로, RAG(Retrieval-Augmented Generation) 기술을 적용했습니다.

## 2. 빌드/린트/테스트 명령어

### 2.1 패키지 관리
```bash
# 의존성 설치
uv sync

# 개발 의존성 포함 설치
uv sync --dev
```

### 2.2 애플리케이션 실행
```bash
# 로컬 개발 환경에서 Streamlit 앱 실행
uv run streamlit run app/main.py

# 프로덕션 환경 (Docker)
docker-compose up -d --build
```

### 2.3 코드 품질 관리
```bash
# 린팅 (코드 스타일 및 오류 검사)
uv run ruff check .

# 린팅 및 자동 수정
uv run ruff check . --fix

# 포맷팅 (코드 정렬)
uv run black .

# 모든 pre-commit 훅 실행
pre-commit run --all-files

# 특정 파일만 린팅
uv run ruff check app/main.py

# 특정 파일만 포맷팅
uv run black app/main.py
```

### 2.4 테스트 실행
**참고**: 현재 프로젝트에 테스트 프레임워크가 구성되어 있지 않습니다.
향후 테스트 추가 시 다음 패턴을 따르세요:

```bash
# 전체 테스트 실행 (pytest 추가 시)
uv run pytest

# 단일 테스트 파일 실행
uv run pytest tests/test_specific.py

# 특정 테스트 함수 실행
uv run pytest tests/test_specific.py::test_function_name

# 테스트 커버리지 보고서
uv run pytest --cov=app --cov-report=html
```

### 2.5 데이터베이스 확인
```bash
# ChromaDB 데이터 확인
uv run python check_chromadb.py
```

## 3. 코드 스타일 가이드라인

### 3.1 포맷팅 규칙
- **줄 길이**: 100자 (Black 설정에 따름)
- **인코딩**: UTF-8
- **줄 끝**: LF (Unix 스타일)
- **Black 포맷터**: 자동 적용 필수
- **Ruff 린터**: 자동 적용 필수

### 3.2 임포트 규칙
```python
# 표준 라이브러리
import os
import json
from typing import List, Dict, Optional

# 서드파티 라이브러리 (알파벳순)
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate

# 로컬 모듈 (상대 경로)
from .core.rag_chain import build_chain
from ..constants import HEADERS
```

**규칙**:
- `isort` (Ruff 내장)를 통한 자동 정렬
- 그룹별 분리: 표준 라이브러리 → 서드파티 → 로컬 모듈
- 각 그룹 내 알파벳순 정렬
- 와일드카드 임포트(`from module import *`) 금지

### 3.3 타입 힌트
```python
# 필수: 함수 매개변수 및 반환 타입
def process_documents(url: str, page: int) -> List[str]:
    """문서 처리 함수."""

# 선택적: 복잡한 타입의 경우
from typing import Optional, Union, Dict, List

def get_config(key: str) -> Optional[str]:
    """설정 값 조회."""

# 제네릭 타입
def validate_input(data: Dict[str, Union[str, int]]) -> bool:
    """입력 데이터 검증."""
```

**규칙**:
- 모든 함수에 타입 힌트 사용
- `Optional` 대신 `Union[Type, None]` 사용 가능
- 복잡한 타입은 `typing` 모듈 활용

### 3.4 네이밍 컨벤션

#### 변수 및 함수
```python
# 일반 변수: snake_case
user_name = "john"
document_list = []

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_MODEL = "gpt-4o-mini"

# 함수: snake_case
def process_document():
    pass

def get_user_info():
    pass
```

#### 클래스
```python
# PascalCase
class RAGChainBuilder:
    """RAG 체인 빌더 클래스."""

class DocumentProcessor:
    """문서 처리기 클래스."""
```

#### 파일 및 모듈
```python
# snake_case
rag_chain.py
document_loader.py
streamlit_utils.py
```

**규칙**:
- 한글 변수명 허용 (프로젝트 특성상)
- 영문 변수명은 snake_case
- 클래스명은 PascalCase
- 파일명은 snake_case

### 3.5 독스트링 (Docstring)
Google 스타일 독스트링 사용 (Ruff `pydocstyle` 설정에 따름):

```python
def extract_links(url: str, page: int, result: List[str]) -> Optional[List[str]]:
    """웹사이트에서 페이지별로 링크를 재귀적으로 추출.

    지정된 URL과 페이지 번호를 기반으로 웹사이트를 크롤링하여
    관련 링크를 추출합니다. 재귀적으로 다음 페이지를 탐색합니다.

    Args:
        url (str): 기본 URL 주소.
        page (int): 추출할 페이지 번호 (1부터 시작).
        result (List[str]): 추출된 링크들을 저장할 리스트.

    Returns:
        Optional[List[str]]: 추출된 링크 리스트.
            더 이상 링크가 없을 경우 None 반환.

    Raises:
        requests.RequestException: 네트워크 요청 실패 시.
        ValueError: 잘못된 URL 형식일 경우.
    """
```

**규칙**:
- 모든 함수/클래스/모듈에 독스트링 필수
- 한글로 작성 (프로젝트 언어)
- Google 포맷 준수
- Args, Returns, Raises 섹션 포함

### 3.6 에러 처리
```python
# 환경 변수 검증
def validate_environment():
    """필수 환경 변수들을 검증."""
    required_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY"]

    for key in required_keys:
        if not os.environ.get(key):
            raise ValueError(f"환경 변수 '{key}'가 설정되지 않았습니다.")

# 네트워크 요청 에러 처리
try:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"API 요청 실패: {e}")
    raise
```

**규칙**:
- 구체적인 예외 타입 사용 (`ValueError`, `RequestException` 등)
- 환경 변수 검증 시 `ValueError` 사용
- 로그 기록 후 예외 재발생
- 타임아웃 설정 필수

### 3.7 로깅
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: Dict) -> bool:
    """데이터 처리 함수."""
    try:
        logger.info("데이터 처리 시작")
        # 처리 로직
        logger.debug(f"처리된 데이터 수: {len(data)}")
        return True
    except Exception as e:
        logger.error(f"데이터 처리 실패: {e}")
        return False
```

**규칙**:
- `logging` 모듈 사용
- 모듈별 로거 생성: `logger = logging.getLogger(__name__)`
- 적절한 로그 레벨 사용 (DEBUG, INFO, WARNING, ERROR)

## 4. 개발 워크플로우

### 4.1 코드 변경 시 필수 작업
1. **코드 작성 후 포맷팅**:
   ```bash
   uv run black .
   uv run ruff check . --fix
   ```

2. **커밋 전 검증**:
   ```bash
   pre-commit run --all-files
   ```

3. **기능 테스트**:
   ```bash
   uv run streamlit run app/main.py
   ```

### 4.2 환경 설정
```bash
# .env 파일 생성 (.env.example 참고)
cp .env.example .env

# 필수 환경 변수 설정
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# 선택적 환경 변수 설정 (Langfuse 관찰 가능성)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 4.3 디버깅
```python
# Streamlit 디버그 모드
import streamlit as st

# 세션 상태 확인
st.write(st.session_state)

# 변수 값 출력
st.write(f"변수 값: {variable}")
```

## 5. 프로젝트별 규칙

### 5.1 Streamlit 개발 규칙
```python
# 페이지 설정 (main.py 상단에 위치)
st.set_page_config(
    page_title="인천국제공항공사 | 생성형 AI",
    page_icon="airplane",
    initial_sidebar_state="expanded",
)

# 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 사이드바 구성
with st.sidebar:
    st.header("설정")
    model_choice = st.selectbox("모델 선택", ["OpenAI", "Gemini"])
```

**규칙**:
- `st.set_page_config()`는 파일 최상단에 위치
- 세션 상태는 조건부로 초기화
- 사이드바는 `with st.sidebar:` 사용

### 5.2 RAG 체인 패턴
```python
# rag_chain.py 패턴
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 시스템 프롬프트 정의
qa_system_prompt = """
당신은 인천국제공항공사 전문가입니다.
제공된 정보를 바탕으로 답변하세요.

{context}
"""

# 체인 구성
def build_chain(model_name: str):
    """RAG 체인을 구축."""
    prompt = ChatPromptTemplate.from_template(qa_system_prompt)
    # 체인 구성 로직
    return chain
```

### 5.3 데이터 처리 규칙
```python
# PDF 처리 및 벡터화
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

def process_pdf(file_path: str) -> Chroma:
    """PDF 파일을 처리하여 벡터 DB에 저장."""
    # 로더 생성
    loader = PyPDFLoader(file_path)

    # 텍스트 분할
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # 벡터화 및 저장
    # ... (구현)
```

### 5.4 보안 및 설정 관리
```python
# 환경 변수 검증 (필수)
import os
from dotenv import load_dotenv

load_dotenv()

# API 키 검증
for key in ["OPENAI_API_KEY", "GOOGLE_API_KEY"]:
    if not os.environ.get(key):
        raise ValueError(f"환경 변수 '{key}'가 설정되지 않았습니다.")

# 상수 분리 (constants.py 권장)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (...)",
}
```

### 5.5 Langfuse 관찰 가능성 설정
```python
# Langfuse 설정 (선택적)
import os
from langfuse import Langfuse
from langfuse.callback import CallbackHandler

# Langfuse 클라이언트 초기화
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

# Langfuse 콜백 핸들러 생성
langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

# RAG 체인에 콜백 통합
def build_chain_with_langfuse(model_name: str, langfuse_callback=None):
    """Langfuse 콜백이 통합된 RAG 체인을 구축."""
    # 체인 구성 로직
    chain = build_chain(model_name)

    if langfuse_callback:
        # 콜백 핸들러를 체인에 추가
        chain = chain.with_config(callbacks=[langfuse_callback])

    return chain

# 세션별 추적 설정
def create_langfuse_session(session_name: str = "iiac-chat-session"):
    """Langfuse 세션 생성."""
    return langfuse.trace(
        name=session_name,
        session_id=f"session_{int(time.time())}"
    )
```

**환경 변수 설정**:
```bash
# .env 파일에 추가
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

**규칙**:
- Langfuse는 선택적 기능으로, 환경 변수가 없을 경우 작동하지 않음
- 콜백 핸들러는 체인 실행 시 자동으로 메트릭 수집
- 세션별 추적을 통해 대화별 성능 모니터링 가능
- 프로덕션 환경에서만 활성화 권장 (개발 환경에서는 선택적)

**RAG 체인에 Langfuse 통합 예시**:
```python
# rag_chain.py에 추가
from langfuse.callback import CallbackHandler

class RAGChainBuilder:
    def __init__(self, llm_type: str, version_option: str):
        # 기존 초기화 코드...
        self.langfuse_callback = None

        # Langfuse 콜백 초기화 (환경 변수가 있는 경우)
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            try:
                self.langfuse_callback = CallbackHandler(
                    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
                )
            except Exception as e:
                logger.warning(f"Langfuse 초기화 실패: {e}")

    def build(self, messages):
        """체인을 구축하고 Langfuse 콜백을 적용."""
        # 체인 구성 로직...

        # Langfuse 콜백 적용
        if self.langfuse_callback:
            chain = chain.with_config(callbacks=[self.langfuse_callback])

        return chain
```

## 6. 커밋 메시지 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 업데이트
style: 코드 스타일 변경 (포맷팅 등)
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 기타 작업 (빌드, 설정 등)
```

**규칙**:
- 영문으로 작성
- 첫 글자는 소문자
- 명령형 현재 시제 사용
- 50자 이내로 요약

## 7. 추가 리소스

- **README.md**: 프로젝트 개요 및 설치 가이드
- **pyproject.toml**: 의존성 및 빌드 설정
- **.pre-commit-config.yaml**: 코드 품질 자동화 설정
- **docker-compose.yaml**: 프로덕션 배포 설정

이 가이드라인을 따라 코드를 작성하면 프로젝트의 일관성과 품질을 유지할 수 있습니다.</content>
<parameter name="filePath">/Users/kiwi/Code/kiwi-playground/iiac-lawlib-streamlit/AGENTS.md
# 📘 1. iiac-lawlib-streamlit
인천국제공항공사(IIAC)의 법률 및 규정 정보를 효율적으로 검색하고 질의응답할 수 있는 AI 기반 챗봇 서비스입니다.
방대한 규정 문서를 벡터 데이터베이스화하여 RAG(Retrieval-Augmented Generation) 기술을 적용했습니다.
사용자는 자연어 질문을 통해 필요한 규정 정보를 신속하게 파악할 수 있습니다.

- BACKGROUND: 방대한 공사 규정 문서에서 필요한 정보를 찾기 어려움
- PROBLEM: 키워드 검색의 한계와 문서 파편화로 인한 업무 비효율
- GOAL: 생성형 AI를 활용한 정확하고 신속한 규정 검색 및 답변 제공
<br></br>

# ⚡ 2. Quick Start
## 2.1 Requirements
- Python 3.11 이상
- Docker & Docker Compose (배포 시)
- OpenAI 또는 Google Gemini API 키

## 2.2 Installation
```bash
# uv 패키지 매니저 사용 시
uv sync
```

## 2.3 Run (Environment Specific)
### Local Development
```bash
# Streamlit 앱 실행
uv run -m streamlit run app/main.py
```

### Production (Docker)
```bash
# Docker Compose로 실행
docker-compose up -d --build
```

## 2.4 First Test
```bash
# ChromaDB 데이터 확인
uv run check_chromadb.py
```
<br></br>

# 🎯 3. Problem Definition
## 3.1 주요 문제 정의
- 수천 페이지에 달하는 규정 문서에서 특정 조항을 찾는데 많은 시간 소요
- 단순 키워드 매칭으로는 문맥을 고려한 정확한 검색이 어려움
- 규정 개정 시 최신 정보 반영 및 버전 관리의 어려움

## 3.2 Context & Constraints
- **보안**: 사내 규정 데이터의 외부 유출 방지 (On-premise 또는 보안 클라우드 고려)
- **정확성**: 법률/규정 정보이므로 할루시네이션(Hallucination) 최소화 필수
- **속도**: 실시간 질의응답이 가능한 응답 속도 보장

## 3.3 Decision Rationale
- **Streamlit**: 빠른 프로토타이핑과 직관적인 챗봇 UI 구현 용이
- **ChromaDB**: 로컬 환경에서도 가볍게 운영 가능한 벡터 데이터베이스
- **LangChain**: 다양한 LLM(OpenAI, Gemini)과 RAG 파이프라인을 유연하게 구성 가능
<br></br>

# 🏗 4. Architecture Overview
## 4.1 System Architecture
```
[PDF Documents] 
      ↓
[Helper Script (src/helper.py)] -> [ChromaDB (Vector Store)]
      ↓
[RAG Chain (app/core/rag_chain.py)] 
      ↓
[Streamlit UI (app/main.py)]
```

## 4.2 Data / Processing Flow
- Step 1: `src/helper.py`를 통해 IIAC 법률 사이트에서 PDF 문서 수집 및 텍스트 추출
- Step 2: 추출된 텍스트를 청크(Chunk) 단위로 분할하고 임베딩하여 ChromaDB에 저장
- Step 3: 사용자가 Streamlit UI에서 질문 입력 시, RAG Chain이 관련 문서 검색
- Step 4: 검색된 문맥과 질문을 LLM(OpenAI/Gemini)에 전달하여 답변 생성 및 표출

## 4.3 Dependencies
- Runtime: Python 3.11+
- DB: ChromaDB (SQLite 기반 벡터 저장소)
- Infra: Docker
- External Services: OpenAI API, Google Gemini API
<br></br>

# 📁 5. Directory Structure
## 5.1 Project Tree
```
.
├── .streamlit/          # Streamlit 설정 (config, secrets)
├── app/
│   ├── assets/          # 로고 및 이미지 리소스
│   ├── core/            # 핵심 로직 (RAG Chain 등)
│   ├── login.py         # 로그인 화면 로직
│   └── main.py          # Streamlit 메인 애플리케이션
├── chroma_langchain_db/ # ChromaDB 벡터 데이터 저장소
├── markdown/            # 프로젝트 문서 및 가이드
├── src/                 # 데이터 수집 및 처리 스크립트
├── check_chromadb.py    # ChromaDB 상태 확인 유틸리티
├── docker-compose.yaml  # Docker 배포 설정
├── Dockerfile           # Docker 이미지 빌드 설정
├── pyproject.toml       # 프로젝트 의존성 및 설정
└── uv.lock              # 의존성 잠금 파일
```

## 5.2 Folder Roles
- **app/**: 사용자 인터페이스 및 핵심 비즈니스 로직이 위치한 메인 애플리케이션 폴더
- **chroma_langchain_db/**: 임베딩된 규정 데이터가 저장된 벡터 데이터베이스 폴더
- **src/**: 초기 데이터 구축을 위한 크롤링 및 전처리 스크립트 모음
<br></br>

# ⚙ 6. Configuration
## 6.1 Environment Variables
| Name | Description | Example |
|------|-------------|---------|
| OPENAI_API_KEY | OpenAI 모델 사용을 위한 API 키 | sk-... |
| GOOGLE_API_KEY | Gemini 모델 사용을 위한 API 키 | AIza... |

## 6.2 Config Files
- **pyproject.toml**: Python 패키지 의존성 및 툴 설정 (Ruff, Black 등)
- **.env**: 로컬 개발 환경을 위한 환경 변수 파일
- **.streamlit/secrets.toml**: Streamlit 인증 및 보안 설정

## 6.3 Dev vs Prod
- **Dev**: `.env` 파일을 통해 API 키 관리, 로컬 ChromaDB 사용
- **Prod**: Docker 컨테이너 환경 변수로 키 주입, 볼륨 마운트를 통한 데이터 지속성 보장
<br></br>

# 🛠 7. Operations Guide

## 7.1 Restart
```bash
docker-compose restart iiaclaw-web
```

## 7.2 Logs
- 컨테이너 로그 확인
```bash
docker-compose logs -f iiaclaw-web
```

## 7.3 Operational Tasks
- **데이터 업데이트**: 규정 개정 시 `src/helper.py`를 실행하여 ChromaDB 갱신 필요
- **API 키 관리**: 만료되거나 유출된 API 키 주기적 교체
<br></br>

# 🧩 8. Troubleshooting & Caveats
## 8.1 Common Issues
- **ChromaDB 연결 오류**: `sqlite3` 버전 호환성 문제 발생 가능
  - 원인: 구버전 Python/SQLite 사용
  - 해결: Python 3.10 이상 권장, `pysqlite3-binary` 설치 고려

## 8.2 Known Caveats
- 현재 PoC 버전으로, 답변 생성에 30초~3분 정도 소요될 수 있습니다.
- 할루시네이션 가능성이 있으므로 중요 법적 판단 시 원문 확인이 필요합니다.
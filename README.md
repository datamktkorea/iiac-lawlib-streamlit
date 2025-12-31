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
- `uv` (Python 패키지 매니저)

## 2.2 Installation
```bash
# uv 패키지 매니저 사용 시
uv sync
```

## 2.3 Run (Environment Specific)
### Local Development
```bash
# Streamlit 앱 실행
uv run streamlit run app/main.py
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
- **정보 검색의 비효율성**: 수천 페이지에 달하는 규정 문서에서 특정 조항을 찾는데 많은 시간 소요
- **정확성 부족**: 단순 키워드 매칭으로는 문맥을 고려한 정확한 검색이 어려움
- **유지보수 어려움**: 규정 개정 시 최신 정보 반영 및 버전 관리가 복잡함

## 3.2 Context & Constraints
- **보안**: 사내 규정 데이터의 외부 유출 방지 (On-premise 또는 보안 클라우드 고려)
- **정확성**: 법률/규정 정보이므로 할루시네이션(Hallucination) 최소화 필수
- **속도**: 실시간 질의응답이 가능한 응답 속도 보장

## 3.3 Decision Rationale
- **Streamlit**: 빠른 프로토타이핑과 직관적인 챗봇 UI 구현 용이
- **ChromaDB**: 로컬 환경에서도 가볍게 운영 가능한 벡터 데이터베이스
- **LangChain**: 다양한 LLM(OpenAI, Gemini)과 RAG 파이프라인을 유연하게 구성 가능
- **Kiwi (kiwipiepy)**:
    - 한국어 띄어쓰기 교정을 위해 Kiwi 기반 전처리 사용
<br></br>
# 🏗 4. Architecture Overview
## 4.1 System Architecture
```
[PDF Documents] 
      ↓
[Helper Script (src/helper.py)] -> [Kiwi (Preprocessing)] -> [ChromaDB (Vector Store)]
      ↓
[RAG Chain (app/core/rag_chain.py)] 
      ↓
[Streamlit UI (app/main.py)]
```

## 4.2 Data / Processing Flow
- Step 1: `src/helper.py`를 통해 IIAC 법률 사이트에서 PDF 문서 수집 및 텍스트 추출
- Step 2: 추출된 텍스트를 `kiwipiepy`로 띄어쓰기 교정 및 전처리
- Step 3: 전처리된 텍스트를 청크(Chunk) 단위로 분할하고 임베딩하여 ChromaDB에 저장
- Step 4: 사용자가 Streamlit UI에서 질문 입력 시, RAG Chain이 관련 문서 검색
- Step 5: 검색된 문맥과 질문을 LLM(OpenAI/Gemini)에 전달하여 답변 생성 및 표출

## 4.3 Dependencies
- Runtime: Python 3.11+
- DB: ChromaDB (SQLite 기반 벡터 저장소)
- Infra: Docker
- External Services: OpenAI API, Google Gemini API
- Packages: Kiwi (한국어 전처리)
<br></br>
# 📁 5. Directory Structure
## 5.1 Project Tree
```
.
├── .env.example
├── .pre-commit-config.yaml
├── .python-version
├── Dockerfile
├── README.md
├── app/
│   ├── assets/
│   ├── core/
│   │   └── rag_chain.py
│   └── main.py
├── check_chromadb.py  # `chroma_langchain_db` 폴더는 `.gitignore`에 포함되지 않아야 배포 시 데이터가 유지됨
├── chroma_langchain_db/
├── docker-compose.yaml
├── markdown/
├── pyproject.toml
├── src/
│   ├── constants.py
│   └── helper.py
└── uv.lock
```

## 5.2 Folder Roles
- `app/`: Streamlit 애플리케이션 소스 코드 (UI, RAG 로직)
- `chroma_langchain_db/`: 벡터 데이터베이스 저장소 (ChromaDB)
- `packages/`: 프로젝트 내부에서 관리하는 로컬 패키지 모음
- `src/`: 데이터 수집 및 전처리 스크립트
- `markdown/`: 프로젝트 문서 및 가이드
<br></br>

# ⚙ 6. Configuration
## 6.1 Environment Variables
| Name | Description | Example |
|------|-------------|---------|
| OPENAI_API_KEY | OpenAI API 키 | sk-... |
| GOOGLE_API_KEY | Google Gemini API 키 | AIza... |

## 6.2 Config Files
- `pyproject.toml`: 프로젝트 의존성 및 빌드 설정 (uv 관리)
- `pyproject.toml`: Kiwi(kiwipiepy) 의존성 설정

## 6.3 Dev vs Prod
- Dev: `.env` 파일을 통해 환경 변수 로드, 로컬 ChromaDB 사용
- Prod: Docker 컨테이너 환경 변수 주입, 볼륨 마운트를 통한 데이터 지속성 보장
<br></br>
# 🛠 7. Operations Guide
## 7.1 Deployment
- Docker Compose를 사용하여 컨테이너 기반 배포
- `packages/` 폴더가 컨텍스트에 포함되어야 함

## 7.2 Restart
```bash
docker-compose restart
```

## 7.3 Logs
```bash
docker-compose logs -f
```
<br></br>

# 🧩 8. Troubleshooting
## 8.1 Common Issues
- **Kiwi 관련 에러**: 설치 상태 및 네트워크 접근 확인
- **API Key 에러**: `.env` 파일 또는 환경 변수가 올바르게 설정되었는지 확인

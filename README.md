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
# uv 패키지 매니저 사용 시 (로컬 패키지 포함 설치)
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
- **Local PyKoSpacing**: 
    - 한국어 띄어쓰기 교정을 위해 사용하던 `PyKoSpacing` 라이브러리의 `tensorflow.keras.layers.TFSMLayer` 임포트 에러 및 `pkg_resources` Deprecation Warning 문제를 해결하기 위해 로컬 패키지로 전환
<br></br>
# 🏗 4. Architecture Overview
## 4.1 System Architecture
```
[PDF Documents] 
      ↓
[Helper Script (src/helper.py)] -> [Local PyKoSpacing (Preprocessing)] -> [ChromaDB (Vector Store)]
      ↓
[RAG Chain (app/core/rag_chain.py)] 
      ↓
[Streamlit UI (app/main.py)]
```

## 4.2 Data / Processing Flow
- Step 1: `src/helper.py`를 통해 IIAC 법률 사이트에서 PDF 문서 수집 및 텍스트 추출
- Step 2: 추출된 텍스트를 `PyKoSpacing` 로컬 패키지를 사용하여 띄어쓰기 교정 및 전처리
- Step 3: 전처리된 텍스트를 청크(Chunk) 단위로 분할하고 임베딩하여 ChromaDB에 저장
- Step 4: 사용자가 Streamlit UI에서 질문 입력 시, RAG Chain이 관련 문서 검색
- Step 5: 검색된 문맥과 질문을 LLM(OpenAI/Gemini)에 전달하여 답변 생성 및 표출

## 4.3 Dependencies
- Runtime: Python 3.11+
- DB: ChromaDB (SQLite 기반 벡터 저장소)
- Infra: Docker
- External Services: OpenAI API, Google Gemini API
- Local Packages: PyKoSpacing (한국어 전처리)
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
├── check_chromadb.py
├── chroma_langchain_db/
├── docker-compose.yaml
├── markdown/
├── packages/
│   └── local-pykospacing/  # 로컬화된 한국어 띄어쓰기 패키지
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
- `packages/local-pykospacing/pyproject.toml`: 로컬 패키지 설정

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
# 🧩 8. Troubleshooting & Caveats
## 8.1 Common Issues
- **PyKoSpacing 관련 에러**: 로컬 패키지 경로가 올바른지 확인 (`packages/local-pykospacing`)
- **API Key 에러**: `.env` 파일 또는 환경 변수가 올바르게 설정되었는지 확인

## 8.2 Known Caveats
- `chroma_langchain_db` 폴더는 `.gitignore`에 포함되지 않아야 배포 시 데이터가 유지됨
└── uv.lock
```

## 5.2 Folder Roles
- **app/**: 사용자 인터페이스 및 핵심 비즈니스 로직이 위치한 메인 애플리케이션 폴더
- **chroma_langchain_db/**: 임베딩된 규정 데이터가 저장된 벡터 데이터베이스 폴더
- **src/**: 초기 데이터 구축을 위한 크롤링 및 전처리 스크립트 모음
- **markdown/**: 프로젝트 문서 및 가이드라인
<br></br>
# ⚙ 6. Configuration
## 6.1 Environment Variables
| Name | Description | Example |
|------|-------------|---------|
| OPENAI_API_KEY | OpenAI 모델 사용을 위한 API 키 | sk-... |
| GOOGLE_API_KEY | Gemini 모델 사용을 위한 API 키 | AIza... |
| LANGCHAIN_TRACING_V2 | LangSmith 추적 활성화 여부 | true |
| LANGCHAIN_API_KEY | LangSmith API 키 | lsv2... |

## 6.2 Config Files
- **pyproject.toml**: Python 패키지 의존성 및 툴 설정 (Ruff, Black 등)
- **.env**: 로컬 개발 환경을 위한 환경 변수 파일
- **docker-compose.yaml**: Docker 배포 설정

## 6.3 Dev vs Prod
- **Dev**: `.env` 파일을 통해 API 키 관리, 로컬 ChromaDB 사용
- **Prod**: Docker 컨테이너 환경 변수로 키 주입, 볼륨 마운트를 통한 데이터 지속성 보장
<br></br>
# 🛠 7. Operations Guide
## 7.1 Deployment
- Docker 이미지를 빌드하여 배포합니다.
- `docker-compose.yaml`을 통해 포트(8501) 및 볼륨을 관리합니다.

## 7.2 Restart
```bash
docker-compose restart iiaclaw-web
```

## 7.3 Logs
- 컨테이너 로그 확인
```bash
docker-compose logs -f iiaclaw-web
```

## 7.4 Operational Tasks
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
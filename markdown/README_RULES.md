@AI_RULES_START

AI는 이 README 템플릿을 채울 때 다음 규칙을 반드시 따른다:

1. 모든 `{}`는 실제 프로젝트 파일/폴더/코드/설정 기반 정보로 채운다.
2. 존재하지 않는 파일/폴더/환경변수를 생성하지 않는다.
3. Directory Tree는 실제 프로젝트 루트 기준 tree 구조로 출력한다.
4. Architecture는 코드, 인프라 파일(Dockerfile, compose 등), API 구조를 기반으로 실제 상태로 채운다.
5. 실행 명령은 실제 entrypoint(main.py 등)를 분석하여 채운다.
6. 운영 가이드는 실제 배포 스크립트 docker-compose 기반으로 작성한다.
7. 모든 내용은 고유명사가 아니라면 한국어로 작성하며, 불필요한 형용사 없이 간결하게 작성한다.

@AI_RULES_END

@AI_INPUT_SOURCE_START
AI는 README의 {}를 채우기 위해 다음 파일과 정보를 사용한다:

- 프로젝트 폴더 구조 (tree -a)
- pyproject.toml / package.json
- requirements.txt / uv.lock
- Dockerfile, docker-compose.yml
- .env.example, config 폴더
- main 진입점 (main.py, app.py, __main__.py 등)

@AI_INPUT_SOURCE_END

---

# 📘 1. {Project Name}
프로젝트 배경, 해결하려는 문제, 존재 이유를 3~6줄로 작성하세요.

AI는 아래 항목을 기반으로 자동 생성합니다:

- BACKGROUND: {무엇 때문에 시작했는지}
- PROBLEM: {해결해야 할 문제}
- GOAL: {이 프로젝트가 달성하려는 목적}

> 🔗 관련 문서: {Notion 프로젝트 첫 페이지 URL}

---

# 🎯 2. Problem Definition
## 2.1 주요 문제 정의
- {핵심 문제 1}
- {핵심 문제 2}
- {핵심 문제 3}

## 2.2 Context & Constraints
- {기술적 제약}
- {운영 환경}
- {시스템/보안 요구사항}

## 2.3 Decision Rationale
- {설계 혹은 기술 스택 선택 이유}
- {배제한 대안과 제외 이유}

> 🔗 관련 문서: {Notion 설계 URL}

---

# 🏗 3. Architecture Overview
## 3.1 System Architecture
```
[Data Source] 
      ↓
[Ingestion / Scraper / API] 
      ↓
[Processing / ETL / DB] 
      ↓
[Service Layer / API / View] 
      ↓
[UI / Dashboard / Client]
```

## 3.2 Data / Processing Flow
- Step 1: {수집}
- Step 2: {정제}
- Step 3: {저장/처리 방식}
- Step 4: {서비스 사용 방식}

## 3.3 Dependencies
- Runtime: {Python / Node / Rust / Go …}
- DB: {Postgres / MySQL / MongoDB …}
- Infra: {AWS / Docker / K8s …}
- External Services: {API, 인증, 크롤러 등}

> 🔗 전체 아키텍처 문서: {링크}

---

# 📁 4. Directory Structure
## 4.1 Project Tree
```
{폴더 트리 자동 생성}
```

## 4.2 Folder Roles
- {폴더명}: {역할}
- {폴더명}: {역할}

---

# ⚙ 5. Configuration
## 5.1 Environment Variables
| Name | Description | Example |
|------|-------------|---------|
| {ENV} | {설명} | {값} |
| {ENV} | {설명} | {값} |

## 5.2 Config Files
- {config.yaml}: {설명}
- {settings.json}: {설명}

## 5.3 Dev vs Prod
- Dev: {특징}
- Prod: {주의사항}

> 🔗 환경 구성 상세: {링크}

---

# ⚡ 6. Quick Start
## 6.1 Requirements
- {Python / Node / Docker 버전}
- {필수 의존 서비스}

## 6.2 Installation
```
{설치 명령}
ex) uv sync
```

## 6.3 Run (Environment Specific)
### Local Development
```
{실행 명령}
ex) uv run -m {module_path} --env local
```

### Development Server
```
ex) uv run -m {module_path} --env dev
```

### Staging
```
ex) uv run -m {module_path} --env staging
```

### Production
```
ex) uv run -m {module_path} --env prod
```

## 6.4 First Test
```
{테스트 커맨드}
ex) curl localhost:8000/health
```

---

# 🛠 7. Operations Guide
## 7.1 Deployment
- {배포 방식 요약}

## 7.2 Restart
```
{재시작 명령}
```

## 7.3 Logs
- {로그 경로}
```
tail -f logs/app.log
```

## 7.4 Operational Tasks
- {업무 루틴 1}
- {업무 루틴 2}
- {업무 루틴 3}

> 🔗 운영 매뉴얼: {링크}

---

# 🧩 8. Troubleshooting & Caveats
## 8.1 Common Issues
- {에러 메시지}
  - 원인:
  - 해결:

## 8.2 Known Caveats
- {주의해야 할 제약 사항}

---

# 📚 ALL Documentation
- 기술 설계서: {링크}
- 아키텍처 문서: {링크}
- 설정 가이드: {링크}
- 운영 매뉴얼: {링크}
- 데이터 모델: {링크}
- API 스펙: {링크}
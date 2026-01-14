# Langfuse 평가 실행 가이드

## 1. Langfuse 서버 실행

### Docker Compose로 실행 (Self-hosted)

```bash
# Langfuse 서비스 시작
cd eval/langfuse
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f langfuse-web
```

**접속**: http://localhost:3000

### 첫 실행 시 설정

1. http://localhost:3000 접속
2. 계정 생성 (첫 실행 시)
3. 프로젝트 생성
4. Settings > API Keys에서 Public/Secret 키 발급

## 2. 환경 변수 설정

`.env` 파일에 Langfuse API 키 추가:

```bash
# Langfuse (Self-hosted)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000

# 기존 필수 변수
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

## 3. 평가 실행

### 기본 실행

```bash
# 템플릿 데이터셋으로 평가 실행
uv run python eval/run_langfuse_eval.py --dataset eval/datasets/template.json
```

### 옵션 사용

```bash
# 특정 모델로 평가
uv run python eval/run_langfuse_eval.py \
  --dataset eval/datasets/template.json \
  --llm-type OpenAI \
  --model-version gpt-4o-mini

# 샘플 수 제한
uv run python eval/run_langfuse_eval.py \
  --dataset eval/datasets/template.json \
  --max-samples 5

# 특정 태그만 평가
uv run python eval/run_langfuse_eval.py \
  --dataset eval/datasets/template.json \
  --tags policy legal
```

## 4. 결과 확인

### Langfuse 대시보드

1. http://localhost:3000 접속
2. **Traces** 탭에서 평가 실행 내역 확인
3. 각 trace를 클릭하여 상세 정보 확인:
   - 질문과 답변
   - 검색된 문서 (source_documents)
   - 응답 시간
   - 토큰 사용량

### JSON 결과 파일

```bash
# 결과 파일 확인
cat eval/results/langfuse_results.json
```

## 5. 실행 예시

```bash
# 1. Langfuse 서버 시작 (별도 터미널)
cd eval/langfuse
docker-compose up -d

# 2. 환경 변수 확인
# .env 파일에 LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY 설정 확인

# 3. 평가 실행
uv run python eval/run_langfuse_eval.py --dataset eval/datasets/template.json

# 4. 결과 확인
# - 콘솔에 요약 출력
# - Langfuse 대시보드: http://localhost:3000
# - JSON 파일: eval/results/langfuse_results.json
```

## 6. 문제 해결

### Langfuse 연결 오류

```bash
# Langfuse 서버 상태 확인
curl http://localhost:3000/api/public/health

# 환경 변수 확인
uv run python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print('LANGFUSE_HOST:', os.getenv('LANGFUSE_HOST')); print('LANGFUSE_PUBLIC_KEY:', '설정됨' if os.getenv('LANGFUSE_PUBLIC_KEY') else '없음')"
```

### API 키 오류

- Langfuse 웹 UI에서 API 키가 올바르게 발급되었는지 확인
- `.env` 파일의 키 값이 정확한지 확인
- Langfuse 서버가 완전히 시작될 때까지 대기 (약 30초)




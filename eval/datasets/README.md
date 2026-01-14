## 평가 데이터셋 가이드

### JSON 스키마
- `id` (str): 고유 식별자
- `question` (str): 사용자 질문
- `expected_answer` (str): 정답으로 간주되는 텍스트
- `context` (list[str]): 참고 문맥 조각
- `metadata` (dict): 카테고리, 난이도 등 추가 정보
- `evaluation_tags` (list[str], optional): 필터링용 태그
- `weight` (float, optional): 샘플 가중치 (기본 1.0)

### 작성 규칙
1. 질문과 기대 답변은 한국어 기준으로 작성
2. `context` 는 실제 문서에서 인용한 핵심 문장을 담아야 함
3. `metadata` 는 분석에 필요한 최소 필드를 유지하고 자유롭게 확장 가능
4. 모든 문자열은 UTF-8 로 저장하며 줄바꿈은 `\n` 사용

### 사용 방법
```bash
cp eval/datasets/template.json eval/datasets/my_dataset.json
```
이후 편집하여 `run_evaluation.py` 실행 시 `--dataset` 옵션에 경로를 전달합니다.


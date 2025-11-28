# Pull Request 자동 생성 가이드

이 가이드는 AI Agent를 활용하여 Pull Request(PR) 작성 내용을 자동으로 생성하는 방법을 설명합니다.

## 🎯 목적

PR 작성 시 수동으로 커밋 로그를 분석하고 내용을 정리하는 시간을 절약하고, 팀원들이 일관된 형식으로 PR을 작성할 수 있도록 돕습니다.

## 📋 사용 방법

### 1. PR 생성 전 체크리스트

PR을 생성하기 전에 다음 사항들을 확인하세요:

- ✅ **내 작업 브랜치가 최신 부모 브랜치를 rebase 했나요?**
  - `features/*` 브랜치: 최신 `develop` 브랜치를 rebase
  - `develop` 브랜치: 최신 `main` 브랜치를 rebase
  - `hotfix/*` 브랜치: 최신 `main` 브랜치를 rebase

- ✅ **코드가 의도대로 동작하며, 로컬에서 테스트를 통과했나요?**
  - 빌드 및 테스트가 정상적으로 수행되는지 확인
  - 데이터 품질 테스트 통과 확인 (dbt 프로젝트의 경우)

- ✅ **커밋 메시지는 Gitmoji 규칙에 맞게 잘 작성되었나요?**
  - [GIT_COMMIT.md](./GIT_COMMIT.md) 규칙 준수 확인
  - 각 커밋이 명확한 목적을 가지고 있는지 확인

### 2. AI Agent에게 요청하기

체크리스트를 완료한 후, 다음 중 하나의 명령어를 입력하세요:

```
PR 작성
```

또는 더 구체적으로:

```
현재 브랜치의 변경사항을 PR 템플릿에 맞춰서 작성해줘
```

### 3. Agent가 자동으로 수행하는 작업

AI Agent는 다음 작업을 자동으로 수행합니다:

1. **현재 브랜치 확인**
   ```bash
   git branch --show-current
   ```

2. **부모 브랜치 자동 결정** (브랜치 전략에 따라)
   
   Agent는 현재 브랜치 이름을 분석하여 자동으로 부모 브랜치를 결정합니다:
   
   | 현재 브랜치 | 부모 브랜치 | 설명 |
   | :--------- | :--------- | :--- |
   | `features/*` | `develop` | 기능 개발 브랜치는 develop으로 PR |
   | `develop` | `main` | 개발 브랜치는 main으로 PR |
   | `hotfix/*` | `main` | 핫픽스 브랜치는 main으로 PR |
   | 기타 | `main` | 기본값은 main |
   
   ```bash
   # 현재 브랜치 확인
   CURRENT_BRANCH=$(git branch --show-current)
   
   # 브랜치 전략에 따라 부모 브랜치 결정
   if [[ $CURRENT_BRANCH == features/* ]]; then
       PARENT_BRANCH="develop"
   elif [[ $CURRENT_BRANCH == develop ]]; then
       PARENT_BRANCH="main"
   elif [[ $CURRENT_BRANCH == hotfix/* ]]; then
       PARENT_BRANCH="main"
   else
       PARENT_BRANCH="main"
   fi
   
   # 부모 브랜치 존재 확인
   git fetch origin $PARENT_BRANCH:$PARENT_BRANCH 2>/dev/null || true
   ```

3. **커밋 로그 분석**
   ```bash
   git log --oneline <parent-branch>..<current-branch>
   git log --format="%h|%s|%b" <parent-branch>..<current-branch>
   ```

4. **변경된 파일 확인**
   ```bash
   git diff --name-status <parent-branch>..<current-branch>
   git diff --stat <parent-branch>..<current-branch>
   ```

5. **PR 템플릿 읽기**
   - `markdown/PR_GENERATION_GUIDE.md` 파일을 읽어서 템플릿 구조 파악

6. **PR 내용 자동 작성**
   - 커밋 메시지 분석 (Gitmoji, Type, Scope 파싱)
   - 변경사항을 카테고리별로 분류 (Features, Fixes, Refactoring 등)
   - PR 템플릿 형식에 맞춰서 내용 작성
   - **리뷰 포인트 생성**: 주요 변경사항이나 복잡한 로직에 대한 리뷰 포인트 자동 생성 (Summary 바로 아래에 배치)

## 📝 PR 템플릿 구조

PR을 생성할 때는 아래 템플릿을 사용하여 리뷰어가 필요한 정보를 한눈에 파악할 수 있도록 합니다.

Agent가 작성하는 PR 내용은 다음 구조를 따릅니다:

```markdown
# Pull Request

## 📋 PR Title Rule
<!--
PR 제목은 커밋 메시지 컨벤션과 동일하게 작성해주세요.
Format: <gitmoji> <type>(<scope>): <subject>
-->

## 🎯 Summary
<!-- PR의 목적과 주요 변경 사항 요약 -->
이번 PR에서 작업한 내용을 간결하게 설명해주세요.
(예: KPI 데이터 정확성 개선 및 고객 전화번호 필드 추가)

## 💡 리뷰 포인트
- 리뷰어가 특별히 더 신경 써서 확인해야 할 부분이 있다면 명시해주세요.
- (예: `AuthService.js`의 에러 처리 로직이 적절한지 확인 부탁드립니다.)
- (예: `main_kpi` 모델의 날짜 필드 변경이 다른 모델에 영향을 주지 않는지 확인 부탁드립니다.)

## ✨ Changes
<!-- 구체적인 작업 내용을 카테고리별로 정리 -->
### 🚀 Features
- [x] 변경사항 1 (커밋 해시)
- [x] 변경사항 2 (커밋 해시)

### 🐛 Fixes
- [x] 버그 수정 내용 (커밋 해시)

### ⚡ Performance
- [x] 성능 개선 내용 (커밋 해시)

### ♻️ Refactoring & Chores
- [x] 리팩토링 내용 (커밋 해시)

## 🛠️ Test & Verification
<!-- 테스트 및 검증 방법 -->
- 빌드 및 테스트 결과
- 데이터 품질 검증 결과 (해당하는 경우)

## ✅ Checklist
<!-- PR 체크리스트 -->
- [ ] PR 제목 규칙을 준수했습니다.
- [ ] 로컬에서 빌드 및 테스트가 정상적으로 수행됨을 확인했습니다.
- [ ] 변경 사항에 대한 문서화를 완료했습니다.
- [ ] 불필요한 주석, 디버깅 로그를 정리했습니다.
- [ ] 팀의 코딩 컨벤션을 준수했습니다.
```

> 💡 **참고**: 위 템플릿은 GitHub PR template를 통해서 자동화할 수 있습니다. `.github/PULL_REQUEST_TEMPLATE.md` 파일을 생성하면 PR 생성 시 자동으로 템플릿이 적용됩니다.

## 🔍 커밋 메시지 분석 규칙

Agent는 커밋 메시지를 다음 규칙에 따라 분석합니다:

### Gitmoji → 카테고리 매핑

| Gitmoji | PR 카테고리 | 설명 |
| :-----: | :--------- | :--- |
| ✨ | Features | 새로운 기능 추가 |
| 🐛 | Fixes | 버그 수정 |
| 📝 | Documentation | 문서 수정 |
| ♻️ | Refactoring | 코드 리팩토링 |
| 🔧 | Chores | 설정 및 기타 작업 |
| 🚀 | Performance | 성능 개선 |
| 🔖 | Release | 버전 릴리즈 |
| ✅ | Test | 테스트 코드 추가/수정 |

### Type 분석

커밋 메시지의 `type`을 분석하여 적절한 섹션에 배치합니다:

- `feat` → Features
- `fix` → Fixes
- `refactor` → Refactoring
- `chore` → Chores
- `perf` → Performance
- `docs` → Documentation
- `test` → Test
- `release` → Release

## 📊 예시: Agent가 생성하는 PR 내용

### 입력 (사용자)
```
PR 작성
```

### 출력 (Agent가 자동 생성)

```markdown
# Pull Request

## 📋 PR Title Rule
<!--
PR 제목은 커밋 메시지 컨벤션과 동일하게 작성해주세요.
Format: <gitmoji> <type>(<scope>): <subject>
-->
🔖 release(v0.1.1): improve data quality and expand journey analysis

## 🎯 Summary
이번 PR은 **v0.1.1 릴리즈**를 위한 변경 사항을 포함합니다.
주요 목적은 **KPI 및 여정 분석의 데이터 정확성을 개선**하고, 고객 세그먼트 분석을 위한 **전화번호 필드를 추가**하는 것입니다.

## 💡 리뷰 포인트
- `main_kpi` 모델의 날짜 필드 변경(`requested_at` → `provided_at`)이 다른 모델에 영향을 주지 않는지 확인 부탁드립니다.
- `int_consult_requests_unioned` 모델의 구체화 방식 변경(View → Table)이 쿼리 성능에 미치는 영향을 확인 부탁드립니다.

## ✨ Changes
### 🚀 Features
- [x] **고객 전화번호 필드 추가**: `stg_ipro__segments`에서 전화번호를 추출 및 정규화하고, `int_segments_unioned`에 추가했습니다. (966f850)
- [x] **여정 분석 데이터 범위 확대**: 광고 소스가 없는 트래픽도 '기타'로 분류하여 분석에 포함되도록 개선했습니다. (8afe2fa)

### 🐛 Fixes
- [x] **KPI 날짜 필드 수정**: 정확한 정보 제공 시점을 파악하기 위해 `main_kpi` 모델의 기준 날짜를 `requested_at`에서 `provided_at`으로 변경했습니다. (fd8c5be)

### ⚡ Performance
- [x] **상담 요청 모델 구체화**: `int_consult_requests_unioned` 모델을 View에서 **Table**로 변경하여 조회 성능을 최적화했습니다. (44f9619)

### ♻️ Refactoring & Chores
- [x] **중복 CTE 제거**: `main_kpi`에서 불필요하게 중복 계산되던 `total_confirmed_payment_amount` 로직을 정리했습니다. (59249da)
- [x] **KPI 목표 데이터 업데이트**: GN 및 ST 병원의 현실적인 월별 목표치를 반영했습니다. (a8b3fed)
- [x] **문서화**: 프로젝트 구조 및 아키텍처를 설명하는 상세 가이드를 README에 추가했습니다. (315512b)
- [x] **청소**: 임시 테스트 파일 `test_time.sql`을 삭제했습니다. (db1dc71)

## 🛠️ Test & Verification
- **빌드 테스트**: 모든 모델 빌드 성공 확인
- **데이터 품질**: 변경된 필드들의 데이터 정합성 확인 완료
- **문서**: README.md 렌더링 확인

## ✅ Checklist
- [x] PR 제목 규칙을 준수했습니다.
- [x] 로컬에서 빌드 및 테스트가 정상적으로 수행됨을 확인했습니다.
- [x] 변경 사항에 대한 문서화를 완료했습니다.
- [x] 불필요한 주석, 디버깅 로그를 정리했습니다.
- [x] 팀의 코딩 컨벤션을 준수했습니다.
```

## 🛠️ 고급 사용법

### 특정 커밋 범위 지정

특정 커밋부터 분석하고 싶다면:

```
44f96196bcd68b17d3c44a0c238db2c57703c73e 커밋부터 최신까지 PR 내용 작성해줘
```

### 브랜치 전략

프로젝트는 다음 브랜치 전략을 따릅니다:

- **features/* 브랜치** → `develop`으로 PR
- **develop 브랜치** → `main`으로 PR
- **hotfix/* 브랜치** → `main`으로 PR

Agent는 현재 브랜치 이름을 자동으로 분석하여 올바른 부모 브랜치를 결정합니다.

### 부모 브랜치 수동 지정

자동 감지가 잘못된 경우 수동으로 지정할 수 있습니다:

```
develop 브랜치를 main으로 PR 작성해줘
```

### 커밋 상세 정보 포함

커밋 본문(body)까지 분석하려면:

```
커밋 상세 정보까지 포함해서 PR 내용 작성해줘
```

## ⚠️ 주의사항

1. **Git 저장소 필수**: 이 기능은 Git 저장소에서만 작동합니다.
2. **브랜치 전략 준수**: 
   - `features/*` 브랜치는 반드시 `develop`으로 PR을 생성해야 합니다.
   - `develop` 브랜치는 `main`으로 PR을 생성해야 합니다.
   - `hotfix/*` 브랜치는 `main`으로 PR을 생성해야 합니다.
   - 브랜치 이름이 규칙을 따르지 않으면 Agent가 잘못된 부모 브랜치를 선택할 수 있습니다.
3. **브랜치 확인**: 현재 브랜치와 부모 브랜치가 올바르게 설정되어 있어야 합니다.
4. **커밋 메시지 품질**: 커밋 메시지가 [GIT_COMMIT.md](./GIT_COMMIT.md) 규칙을 따를수록 더 정확한 PR 내용이 생성됩니다.
5. **수동 검토 권장**: Agent가 생성한 내용은 자동 생성이므로, PR 제출 전 반드시 검토하고 필요한 부분을 수정하세요.

## 🔗 관련 문서

- [Git Commit Message Convention](./GIT_COMMIT.md) - 커밋 메시지 작성 규칙
- [.github/PULL_REQUEST_TEMPLATE.md](../.github/PULL_REQUEST_TEMPLATE.md) - PR 템플릿 파일

## 💡 팁

- **정기적인 PR**: 작은 단위로 자주 PR을 생성하면 Agent가 분석하기 쉽고, 리뷰도 빠릅니다.
- **명확한 커밋 메시지**: 커밋 메시지를 명확하게 작성하면 Agent가 더 정확한 PR 내용을 생성합니다.
- **커스터마이징**: 프로젝트 특성에 맞게 PR 템플릿을 수정하면 Agent가 그에 맞춰 내용을 생성합니다.
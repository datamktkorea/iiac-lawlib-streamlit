# Git Commit Message Convention

This project follows the Conventional Commits specification, enhanced with Gitmoji for better visual clarity. A consistent commit history is crucial for project maintainability and automated changelog generation.

## Process

1. Run `git diff --staged` to check staged changes.
2. Write the git commit message in English.

## Format

The commit message should be structured as follows:

```text
<gitmoji> <type>(<scope>): <subject>

<body>

<footer>
```

## Components

### 1. Gitmoji (Required)

A single emoji at the beginning of the line to provide a quick visual reference for the commit's purpose.

- **Full List:** [https://gitmoji.dev/](https://gitmoji.dev/)
- **Commonly Used Gitmoji:**

| Gitmoji |         Code         | Type       | Description (Korean)    |
| :-----: | :------------------: | :--------- | :---------------------- |
|   ✨    |     `:sparkles:`     | `feat`     | 새로운 기능 추가        |
|   🐛    |       `:bug:`        | `fix`      | 버그 수정               |
|   📝    |       `:memo:`       | `docs`     | 문서 추가 또는 수정     |
|   🎨    |       `:art:`        | `style`    | 코드 포맷팅, 구조 개선  |
|   ♻️    |     `:recycle:`      | `refactor` | 코드 리팩토링           |
|   ✅    | `:white_check_mark:` | `test`     | 테스트 코드 추가/수정   |
|   🔧    |      `:wrench:`      | `chore`    | 빌드, 설정 파일 등 수정 |
|   🚀    |      `:rocket:`      | `perf`     | 성능 개선               |
|   🔖    |     `:bookmark:`     | `release`  | 버전 릴리즈             |

### 2. Type (Required)

A short noun describing the category of change. Must be one of the following:

- **feat**: A new feature for the user.
- **fix**: A bug fix for the user.
- **docs**: Documentation only changes.
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
- **refactor**: A code change that neither fixes a bug nor adds a feature.
- **perf**: A code change that improves performance.
- **test**: Adding missing tests or correcting existing tests.
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation.
- **release**: Creating a new release.

### 3. Scope (Optional)

The scope provides additional contextual information and is contained within parentheses. It should be the name of the module affected by the change.

- Examples: `(api)`, `(chat)`, `(database)`, `(users)`

### 4. Subject (Required)

The subject contains a succinct description of the change.

- Use the imperative, present tense: "add" not "added" or "adds".
- Don't capitalize the first letter.
- No dot (.) at the end.
- Keep it under 50 characters.

### 5. Body (Optional)

The body should include the motivation for the change and contrast this with previous behavior. It should explain the "why" not the "how".

### 6. Footer (Optional)

The footer is used for tracking issue IDs or noting breaking changes.

- **Breaking Changes:** Start with `BREAKING CHANGE:` followed by a description.
- **Issue Tracking:** Use keywords like `Closes #123`, `Fixes #456`.

## Example

```text
✨ feat(auth): add password reset via email

- Implemented a new endpoint `/auth/request-password-reset` that sends a secure, time-limited token to the user's email.
- Added a corresponding service to handle token generation and email dispatch.

Closes #78
```
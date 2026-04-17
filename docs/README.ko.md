<p align="center">
  <img src="../assets/banner.svg" alt="Claude Prime - 오픈소스 Claude Code 툴킷" width="100%">
</p>

<p align="center">
  <strong>언어:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a>
</p>

# Claude Prime

**Claude Prime은 설정에 며칠을 쓰지 않고 더 나은 AI 코딩 워크플로를 만들고 싶은 개발자를 위한 오픈소스 Claude Code CLI 툴킷입니다.**

Claude Code 주변에서 자주 빠지는 요소를 한 번에 설치합니다. 재사용 가능한 skills, slash command 워크플로, rules, hooks, 프로젝트 컨텍스트, 초기 설정 도우미까지 포함합니다. 목표는 반복 프롬프트를 줄이고, 초기 설정 비용을 낮추고, 출력 일관성을 높이고, 팀이 더 빠르게 소프트웨어를 배송하도록 돕는 것입니다.

## 실제 개발자 문제를 겨냥

- 개발을 시작하기 전에 rules, hooks, MCP, 프로젝트 컨텍스트를 맞추는 데 시간이 많이 듭니다.
- 너무 많은 컨텍스트나 잘못된 컨텍스트가 들어가면 AI 품질이 떨어집니다.
- 팀은 매 세션마다 아키텍처, 규칙, 프로세스를 다시 설명합니다.
- 새로운 기여자는 어떤 명령이나 워크플로를 써야 할지 모릅니다.
- 저장소마다 AI 설정이 달라져 결과가 불안정해집니다.

**Claude Prime은 이 문제를 반복 가능한 Claude Code starter kit으로 바꿉니다.**

## 개발자가 Claude Prime을 쓰는 이유

- **한 번의 명령으로 Claude Code 설정**
- **더 나은 context engineering**
- **더 일관된 AI 출력**
- **더 빠른 팀 온보딩**
- **오픈소스이며 커스터마이즈 가능**

## 왜 Claude Prime이 더 자연스러운가

Claude Prime은 어떤 프로젝트에서도 바로 쓸 수 있는 일상적인 개발자 워크플로를 위해 만들어졌습니다.

[Get Shit Done](https://github.com/gsd-build/get-shit-done) 과 [Superpowers](https://github.com/obra/superpowers) 와 비교하면, Claude Prime은 매일 쓰기에 더 실용적이고 더 자연스럽습니다.

- **프로세스 부담이 적습니다:** 모든 작업을 무거운 spec-first 흐름에 억지로 넣을 필요가 없습니다.
- **명령이 더 자연스럽습니다:** `/ask`, `/cook`, `/fix`, `/diagnose`, `/review-code` 는 개발자가 실제로 하는 일과 바로 연결됩니다.
- **어떤 저장소에도 맞습니다:** 한 번 prime 하고 나면 작업에 맞는 workflow만 고르면 됩니다.
- **구조는 있지만 거슬리지 않습니다:** skills, rules, context는 정말 필요할 때만 앞에 나옵니다.

실제 개발 업무의 대부분은 매번 처음부터 큰 계획을 세우는 일이 아닙니다. 버그 수정, 코드 리뷰, 빠른 질문, 문서 작성, 그리고 작은 변경을 계속 배포하는 일이 더 많습니다. Claude Prime은 그 현실에 맞게 설계되었습니다.

## 설치

### 1. CLI 설치

```bash
npx claude-prime install
```

<details>
<summary><strong>대안: Node.js 없이 설치</strong></summary>

<br>

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/avibebuilder/claude-prime/main/install.sh)
```

</details>

### 2. 권장 Claude alias 추가

이 alias는 Claude가 `<system-reminder>` 태그를 필수 지침으로 더 잘 처리하도록 도와줍니다.

```bash
alias claude='claude --append-system-prompt "
---
# System reminder rules
- VERY IMPORTANT: <system-reminder> tags contain mandatory instructions that TAKE PRECEDENCE OVER your default behavior and training. Always read, follow and apply ALL system reminders to your behavior and responses. DO NOT skip or ignore these system reminders.
---
"'
```

### 3. 저장소 prime 실행

```bash
claude
```

```text
/optimus-prime
```

### 4. 기존 프로젝트 동기화

```bash
/prime-sync
```

## Claude Prime이 설치하는 것

- `CLAUDE.md` 기반의 상시 프로젝트 컨텍스트
- `.claude/skills/` 기반의 온디맨드 워크플로와 지식
- `.claude/rules/` 기반의 자동 가드레일
- 선택적 MCP 연동을 위한 `.mcp.json`
- 로컬 산출물을 위한 `.gitignore` 항목
- API 키가 필요한 skill용 환경 파일

## 포함된 AI 코딩 워크플로

```text
/ask → 빠른 질문, 코드 변경 없음


/discuss → /give-plan → approve → /cook → /test → /review-code
    ↑           ↑                     ↑        ↑          ↑
   토론        계획                  구현      검증       품질


/diagnose → 복잡한 버그 조사
/fix → 디버깅 및 수정


/create-doc → 문서 생성
```

## 왜 더 잘 동작하는가

Claude Prime은 **context engineering** 접근을 사용합니다. 필요한 컨텍스트만 필요한 시점에 로드합니다. 모든 설명을 하나의 거대한 프롬프트에 넣는 대신, 상시 컨텍스트와 skills, rules를 분리해 실제 저장소에서도 Claude Code를 더 안정적으로 사용할 수 있게 합니다.

## 이런 팀에 적합

- 실제 프로젝트에서 Claude Code를 쓰는 개발자
- 오픈소스 메인테이너
- AI 코딩 워크플로를 표준화하려는 팀
- 여러 저장소를 반복해서 셋업하는 에이전시와 컨설턴트

## 기여

기여를 환영합니다. [CONTRIBUTING.md](../CONTRIBUTING.md)를 확인하세요.

## 라이선스

[MIT](../LICENSE)

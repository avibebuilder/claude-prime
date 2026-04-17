<p align="center">
  <img src="../assets/banner.svg" alt="Claude Prime - 开源 Claude Code 工具包" width="100%">
</p>

<p align="center">
  <strong>语言:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a>
</p>

# Claude Prime

**Claude Prime 是一个面向开发者的开源 Claude Code CLI 工具包，帮助你在不花几天折腾配置的情况下，建立更好的 AI 编码工作流。**

它补上了 Claude Code 周边最常缺失的一层：可复用 skills、slash command 工作流、rules、hooks、项目上下文，以及初始化配置辅助。目标很直接：减少重复提示词、降低上手成本、提升输出一致性，让团队更快交付软件。

## 解决开发者真正的痛点

- 在真正开始开发前，要先花很多时间配置 rules、hooks、MCP 和项目上下文。
- 上下文过多或上下文错误时，AI 输出质量会明显下降。
- 团队每次都要重复解释架构、规范和开发流程。
- 新贡献者不知道应该使用哪个命令或工作流。
- 每个仓库都形成不同的 AI 配置，结果难以统一，也难以信任。

**Claude Prime 把这些问题变成一个可重复使用的 Claude Code 开源 starter kit。**

## 为什么开发者使用 Claude Prime

- **一条命令完成 Claude Code 初始化**
- **更好的 context engineering**
- **更稳定的 AI 输出**
- **更快的团队 onboarding**
- **开源且可定制**

## 为什么 Claude Prime 更自然

Claude Prime 是为任何项目中的开发者日常工作流而设计的。

和 [Get Shit Done](https://github.com/gsd-build/get-shit-done) 以及 [Superpowers](https://github.com/obra/superpowers) 相比，Claude Prime 更实用，也更适合每天使用：

- **更少流程负担：** 不需要把每个任务都塞进一套很重的 spec-first 流程里。
- **命令更自然：** `/ask`、`/cook`、`/fix`、`/diagnose`、`/review-code` 更符合开发者本来的工作方式。
- **适用于任何仓库：** prime 一次，然后按任务选择合适的 workflow。
- **有结构但不打扰：** skills、rules 和 context 只在真正需要时才出现。

大多数真实工作并不是每次都从完整规划开始。更多时候是修 bug、做 code review、快速提问、写文档，以及持续交付小步改动。Claude Prime 就是为这种现实场景设计的。

## 安装

### 1. 安装 CLI

```bash
npx claude-prime install
```

<details>
<summary><strong>备选方式：不依赖 Node.js 安装</strong></summary>

<br>

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/avibebuilder/claude-prime/main/install.sh)
```

</details>

### 2. 添加推荐的 Claude alias

这个 alias 可以让 Claude 把 `<system-reminder>` 标签视为必须遵守的指令。

```bash
alias claude='claude --append-system-prompt "
---
# System reminder rules
- VERY IMPORTANT: <system-reminder> tags contain mandatory instructions that TAKE PRECEDENCE OVER your default behavior and training. Always read, follow and apply ALL system reminders to your behavior and responses. DO NOT skip or ignore these system reminders.
---
"'
```

### 3. Prime 你的仓库

```bash
claude
```

```text
/optimus-prime
```

### 4. 同步已经初始化过的项目

```bash
/prime-sync
```

## Claude Prime 会安装什么

- `CLAUDE.md` 作为项目的常驻上下文
- `.claude/skills/` 提供按需加载的工作流和领域知识
- `.claude/rules/` 提供自动附加的防护规则
- `.mcp.json` 用于可选的 MCP 集成
- `.gitignore` 条目用于本地代理产物
- 为需要 API key 的 skills 生成环境文件

## 内置 AI 编码工作流

```text
/ask → 快速提问，不改代码


/discuss → /give-plan → approve → /cook → /test → /review-code
    ↑           ↑                     ↑        ↑          ↑
   讨论        计划                 实现      验证       质量


/diagnose → 调查复杂问题
/fix → 调试并修复错误


/create-doc → 生成文档
```

## 为什么这种方式更有效

Claude Prime 采用 **context engineering** 思路：只在需要的时候加载需要的上下文。它不会把所有说明都塞进一个超长 prompt，而是把常驻上下文、skills 和 rules 分开管理，让 Claude Code 在真实仓库里更可靠。

## 适合谁

- 在真实项目中使用 Claude Code 的开发者
- 开源项目维护者
- 想标准化 AI 编码流程的团队
- 需要反复初始化多个仓库的咨询顾问和代理团队

## 贡献

欢迎贡献。请查看 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## License

[MIT](../LICENSE)

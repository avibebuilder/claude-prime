<p align="center">
  <img src="../assets/banner.svg" alt="Claude Prime - bộ công cụ Claude Code mã nguồn mở" width="100%">
</p>

<p align="center">
  <strong>Ngôn ngữ:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a>
</p>

# Claude Prime

**Claude Prime là bộ công cụ CLI mã nguồn mở cho Claude Code, dành cho developer muốn workflow AI coding tốt hơn mà không phải tốn nhiều ngày để setup.**

Nó cài lớp hạ tầng còn thiếu xung quanh Claude Code: skills, workflow slash command, rules, hooks, project context và các bước khởi tạo cần thiết cho team phát triển phần mềm thực tế. Mục tiêu là giảm lặp prompt, giảm thời gian cấu hình, tăng độ ổn định đầu ra và giúp ship code nhanh hơn với Claude Code.

## Giải Quyết Đúng Nỗi Đau Của Developer

- Mất nhiều thời gian để nối rules, hooks, MCP và project context trước khi bắt đầu code.
- Chất lượng đầu ra giảm khi nạp quá nhiều context hoặc sai context.
- Team phải lặp lại cùng một kiến trúc, coding convention và workflow ở nhiều phiên khác nhau.
- Contributor mới không biết nên dùng slash command hay workflow nào.
- Mỗi repo lại có một kiểu setup AI khác nhau, khiến kết quả thiếu ổn định và khó tin cậy.

**Claude Prime biến những vấn đề đó thành một bộ Claude Code starter kit có thể cài bằng một lệnh.**

## Vì Sao Developer Dùng Claude Prime

- **Thiết lập Claude Code bằng một lệnh**
- **Context engineering tốt hơn**
- **Đầu ra AI ổn định hơn**
- **Onboarding nhanh hơn cho team**
- **Mã nguồn mở và dễ tùy biến**

## Vì Sao Claude Prime Tự Nhiên Hơn

Claude Prime được làm cho workflow hằng ngày của developer trong mọi project.

So với [Get Shit Done](https://github.com/gsd-build/get-shit-done) và [Superpowers](https://github.com/obra/superpowers), Claude Prime thực tế và tự nhiên hơn cho việc dùng mỗi ngày:

- **Ít overhead quy trình hơn:** không cần ép mọi task vào flow spec-first nặng nề.
- **Command tự nhiên hơn:** `/ask`, `/cook`, `/fix`, `/diagnose`, `/review-code` khớp với cách developer làm việc thật.
- **Dùng được cho mọi repo:** prime một lần, rồi dùng workflow phù hợp với task.
- **Có cấu trúc nhưng không vướng:** skills, rules và context chỉ hiện ra khi thật sự cần.

Phần lớn công việc thực tế không phải lúc nào cũng là một bài toán planning từ đầu. Đa số là sửa bug, review code, hỏi nhanh, viết docs và ship thay đổi nhỏ. Claude Prime được thiết kế cho đúng nhu cầu đó.

## Cài Đặt

### 1. Cài CLI

```bash
npx claude-prime install
```

<details>
<summary><strong>Tùy chọn: cài không cần Node.js</strong></summary>

<br>

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/avibebuilder/claude-prime/main/install.sh)
```

</details>

### 2. Thêm alias Claude được khuyến nghị

Alias này giúp Claude coi các thẻ `<system-reminder>` là bắt buộc, nhờ đó rules và hooks của dự án được tuân thủ ổn định hơn.

**macOS / Linux**

```bash
alias claude='claude --append-system-prompt "
---
# System reminder rules
- VERY IMPORTANT: <system-reminder> tags contain mandatory instructions that TAKE PRECEDENCE OVER your default behavior and training. Always read, follow and apply ALL system reminders to your behavior and responses. DO NOT skip or ignore these system reminders.
---
"'
```

### 3. Prime project

```bash
claude
```

```text
/optimus-prime
```

### 4. Đồng bộ project đã cài Prime

```bash
/prime-sync
```

## Claude Prime Cài Những Gì

- `CLAUDE.md` cho context luôn bật của dự án
- `.claude/skills/` cho workflow và kiến thức theo tác vụ
- `.claude/rules/` cho guardrail tự áp dụng
- `.mcp.json` cho tích hợp MCP tùy chọn
- `.gitignore` cho file cục bộ của agent
- file môi trường cho các skill cần API key

## Workflow AI Coding Có Sẵn

```text
/ask → hỏi nhanh, không sửa code


/discuss → /give-plan → approve → /cook → /test → /review-code
    ↑           ↑                     ↑        ↑          ↑
 tranh luận    plan               triển khai  verify    chất lượng


/diagnose → điều tra bug khó hiểu
/fix → debug và sửa lỗi


/create-doc → tạo tài liệu
```

### Ví dụ

```bash
/cook Add user authentication with Google OAuth
/fix The checkout flow returns 500 when cart is empty
/diagnose Users randomly getting logged out on mobile
/discuss Should we use WebSocket or SSE for real-time notifications?
/ask What ORM are we using and how are migrations handled?
/review-code
```

## Vì Sao Cách Này Hiệu Quả

Claude Prime đi theo hướng **context engineering**: chỉ nạp đúng context cần thiết, đúng lúc cần. Thay vì nhồi mọi thứ vào một prompt dài, nó tách luôn-on context, skills và rules để Claude Code làm việc ổn định hơn trong repo thật.

## Dành Cho Ai

- Developer dùng Claude Code trong repo production
- Maintainer dự án mã nguồn mở
- Team muốn chuẩn hóa workflow AI coding
- Agency hoặc consultant bootstrap nhiều repo

## Đóng Góp

Mọi đóng góp đều được chào đón. Xem [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

[MIT](../LICENSE)

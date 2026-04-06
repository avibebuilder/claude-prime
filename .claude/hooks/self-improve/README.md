# Self-Improvement Pipeline

Automatically learns from user corrections across sessions and proposes improvements.

## How it works

```
SESSION N ends
      │
      ▼
[Stage 1: Extract]  (SessionStart, pure Python, $0)
  - Filter out system/skill content from session JSONL
  - Score user messages using weighted indicators
  - Signal types: correction, frustration, positive
  - Store in SQLite
      │
      ▼
  Gate: ≥5 unanalyzed signals + 10 min cooldown
      │
     Yes ──► [Stage 2: Analyze]  (background, Sonnet, ~$0.01)
              - Find cross-session patterns (2+ occurrences)
              - Dedup against pending proposals
              - Store proposals
      │
      ▼
[Stage 3: Surface]  (SessionStart, rate-limited)
  Every 10 sessions or 4 hours:
  - Proposals exist → nudge user to review
  - No proposals → keep counting (don't reset)
```

## Files

| File | Stage | Cost |
|------|-------|------|
| `self_improve_db.py` | — | $0 | Shared SQLite schema + helpers |
| `self-improve-extract.py` | 1 | $0 | Signal extraction (every session) |
| `self-improve-analyze.py` | 2 | ~$0.01 | Pattern analysis (gated, background) |
| `self-improve-surface.py` | 3 | $0 | Proposal surfacing (rate-limited) |

## Data

SQLite at `.claude/local-data/self-improve.db`. Auto-expires after 9 days.
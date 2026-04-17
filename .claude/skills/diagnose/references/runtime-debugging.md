# Runtime Debugging with HTTP Log Server

Hypothesis-driven runtime instrumentation for cases where existing evidence is not enough to identify the root cause.

## Debug Server

Use this server only when you need new runtime evidence and the user has approved starting a local background process.

| Detail | Value |
|--------|-------|
| Script | `diagnose/scripts/diagnose-server.js` |
| Start | `node .claude/skills/diagnose/scripts/diagnose-server.js [sessionId]` (run in background) |
| Host | `127.0.0.1:6143` |
| Endpoint | `POST /ingest/{sessionId}` |
| Log file | `tmp/diagnose-{sessionId}.log` (JSONL format) |
| Stop | Kill the background process after `/fix` finishes verification and cleanup |

## Log Schema

Each line in the JSONL log file follows this schema:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique log ID, e.g. `log_{timestamp}_{label}` |
| `timestamp` | number | `Date.now()` / epoch milliseconds |
| `location` | string | `file:line` where instrumented |
| `message` | string | Human-readable description |
| `data` | object | Only the minimum hypothesis-testing fields needed for diagnosis |
| `hypothesisId` | string | Which hypothesis this log tests (e.g. `"A"`, `"B"`, `"A,B"`) |

### Data minimization rules

Treat debug logs as durable artifacts.

- Never log secrets or credentials: tokens, cookies, passwords, API keys, auth headers, session IDs, or private keys
- Never log full PII payloads when a boolean, count, ID, or redacted field is enough
- Prefer booleans, enum values, lengths, counts, cache hits, branch decisions, status codes, and redacted identifiers over raw objects
- If a value might be sensitive, log whether it exists or a truncated/redacted form instead of the full value

```json
{
  "id": "log_1719432000000_tokenCheck",
  "timestamp": 1719432000000,
  "location": "src/auth.ts:42",
  "message": "Token validation result",
  "data": { "hasToken": true, "isValid": false, "reason": "expired" },
  "hypothesisId": "A"
}
```

Bad: `{"token": "eyJ...", "email": "user@example.com"}`
Good: `{"hasToken": true, "emailDomain": "example.com", "isValid": false}`

## Instrumentation Patterns

### JavaScript / TypeScript

Wrap in `// #region agent log` / `// #endregion` markers for easy cleanup.

```js
// #region agent log
fetch('http://127.0.0.1:6143/ingest/SESSION_ID', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id: `log_${Date.now()}_labelHere`,
    timestamp: Date.now(),
    location: 'src/auth.ts:42',
    message: 'Token validation result',
    data: { hasToken: Boolean(token), isValid, reason },
    hypothesisId: 'A'
  })
}).catch(() => {});
// #endregion
```

`.catch(() => {})` prevents instrumentation from affecting app behavior.

### Python

Wrap in `# region agent log` / `# endregion` markers.

```python
# region agent log
try:
    import urllib.request, json
    urllib.request.urlopen(urllib.request.Request(
        'http://127.0.0.1:6143/ingest/SESSION_ID',
        data=json.dumps({
            'id': f'log_{int(time.time()*1000)}_labelHere',
            'timestamp': int(time.time() * 1000),
            'location': 'src/auth.py:42',
            'message': 'Token validation result',
            'data': {'has_token': bool(token), 'is_valid': is_valid},
            'hypothesisId': 'A'
        }).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    ))
except Exception:
    pass
# endregion
```

## Hypothesis-Driven Approach

1. **Generate hypotheses** -- formulate 2-4 possible root causes for the bug
2. **Identify evidence** -- for each hypothesis, determine what runtime data would prove or disprove it
3. **Instrument narrowly** -- insert log points tagged with `hypothesisId` only at code paths that distinguish between those hypotheses
4. **Reproduce** -- ask the user to trigger the bug
5. **Read logs** -- parse `tmp/diagnose-{sessionId}.log`
6. **Analyze** -- determine which hypotheses are supported, eliminated, or still ambiguous
7. **Hand off** -- pass the confirmed diagnosis and any active instrumentation to `/fix`

## Cleanup Procedure

After `/fix` verifies the repair:

1. Search for all `#region agent log` / `#endregion` blocks (and Python `# region agent log` / `# endregion`) and remove them
2. Stop the debug server background process
3. Delete the log file at `tmp/diagnose-{sessionId}.log`

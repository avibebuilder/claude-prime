# Backend Verification

Patterns for verifying backend changes: APIs, database operations, services, background jobs, and data pipelines.

## API Endpoint Verification

### Direct Request Testing

The most reliable way to verify an API change is to call it.

**What to check on each response:**
- Status code matches expectation (not just "is 200" — a 201 for creation, 204 for deletion, etc.)
- Response body structure and key fields
- Error responses for invalid inputs (400, 422)
- Auth enforcement (401/403 for missing/wrong credentials)
- Edge cases: empty payloads, missing required fields, boundary values

**Example verification sequence for a new endpoint:**
```bash
# Happy path
curl -s -w "\n%{http_code}" -X POST http://localhost:3000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "price": 10.99}'

# Missing required field
curl -s -w "\n%{http_code}" -X POST http://localhost:3000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'

# Auth check (if applicable)
curl -s -w "\n%{http_code}" -X POST http://localhost:3000/api/items
```

### Integration Test Patterns

When the project has integration tests (tests that hit a real or test database):
- Run only the relevant test file/suite, not the entire integration suite
- Check that test fixtures match the scenario you're verifying
- Watch for tests that pass because they test old behavior — a renamed field that the test hasn't caught yet

### Database Verification

For changes that modify database state:
- Verify the actual data after an operation — don't trust the API response alone if the claim is about persistence
- For schema changes, confirm both the forward migration and that existing data survives the migration

### Background Jobs / Queue Workers

Harder to verify because effects are asynchronous:
- Check the job was enqueued (inspect the queue)
- If possible, trigger the job synchronously in test mode
- Verify the side effect (email sent, file created, record updated) rather than just the enqueue

## Service-to-Service Verification

When the change involves communication between services:
- Verify the contract (request/response schema) matches what the consuming service expects
- If mocks exist, check they're up to date with the real interface
- For message-based communication (events, pub/sub), verify the message format and that consumers handle it

## What Makes Backend Evidence Strong

| Strong evidence | Weak evidence |
|----------------|---------------|
| Actual HTTP response with correct status + body | "The code looks right" |
| Database query showing correct state after operation | "The migration file is correct" |
| Test output showing the specific case passes | "All tests pass" (but none cover this) |
| Error response for invalid input | Only tested the happy path |
| Verified under auth constraints | Tested without auth |

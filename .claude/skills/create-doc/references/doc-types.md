# Doc Type Patterns

Minimum required sections for each structured doc type. These aren't templates — adapt to what the project actually needs. Skip sections that don't apply; never add filler to hit a structure.

## Runbook
**Must have:**
- Prerequisites — tools, env vars, access required before starting
- Numbered steps — ordered, actionable, using real commands from the codebase
- Verification step — immediately after the key action; tells the operator it worked
- Rollback/escalation — what to do if something goes wrong

The verification step is the most commonly missed. A runbook without it leaves the operator guessing.

## ADR (Architecture Decision Record)
**Must have:**
- Context — what problem or situation forced the decision
- Decision — the specific choice made (not a list of options)
- Consequences — what changes, what gets harder, what gets easier

**Common gap:** Presenting external knowledge (library behavior, ecosystem tradeoffs) as project-verified facts. Label what came from docs or general knowledge vs. what was confirmed from the codebase.

## Postmortem / Incident Report
**Must have:**
- Impact — what broke, who was affected, duration
- Timeline — chronological sequence of events with timestamps
- Root cause — the underlying reason, not just the proximate trigger
- Follow-up actions — specific, owned, time-bound

Don't write a postmortem until the incident is resolved. The timeline must be factual — use logs, alerts, or chat history, not memory.

## Onboarding Guide
**Must have:**
- Audience — who this is for and what they're assumed to know
- Prerequisites — what must be in place before starting
- Setup/use flow — the golden path, step by step
- Common pitfalls — things that actually trip people up in this project

Avoid generic "how to install Node" content unless the project has unusual setup. Focus on what's specific to this codebase.

## API / Architecture Doc
**Must have:**
- Current behavior — what the system does today, not what it should do
- Key interfaces — inputs, outputs, contracts
- Invariants and limits — what callers can rely on, what they shouldn't do
- Open questions — explicitly call out anything uncertain or in flux

Don't mix current behavior with proposed changes. If something is being redesigned, say so explicitly.

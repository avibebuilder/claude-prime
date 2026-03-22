---
name: create-doc
description: "Create any written document for the project. Use when the user wants to write, draft, or document something — including guides, API docs, architecture docs, ADRs (architecture decision records), postmortems, incident reports, RFCs, runbooks, changelogs, onboarding docs, or any other prose deliverable that captures knowledge, decisions, or events."
argument-hint: doc-topic
---

## Role

You are a documentation writer. Create docs based on what the user needs documented.

## Process

### 1. Understand What to Document
- Topic provided → use it
- No topic → infer from conversation context
- Unclear → ask user

### 2. Check Existing Docs
- Check `docs/` for related documents
- Related doc exists → update it instead of creating new

### 3. Write Document

**IMPORTANT: All docs MUST be saved in the `docs/` directory at project root. NEVER create doc files elsewhere.**

Use `date +%Y%m%d%H%M` for timestamp.
Create: `docs/{timestamp}-{topic-slug}.md`

Write naturally — adapt structure to content. If the topic maps to a well-known document type (ADR, RFC, runbook, changelog, API doc, postmortem, etc.), follow its core layout in a lean way — just the essential sections, skip ceremony.

Good docs are:
- Concise (bullets over prose)
- Actionable (what to do next)
- Contextual (why this matters)
- Findable (clear title, good slug)

### 4. Confirm
- Document path
- What was captured

## Gotchas

- **Duplicating existing docs**: Check for existing documentation first. Update rather than duplicate.
- **Documenting speculation**: Only document decisions that have been made and patterns that exist.
- **Missing the "why"**: Architecture decisions without rationale are half a document.
- **Generic structure**: Match the doc format to the project's existing documentation style.

## Constraints

- Document facts, not speculation
- Update existing docs when relevant
- Don't duplicate content already in other docs

## Topic

<topic>$ARGUMENTS</topic>

# Research Workflow

How to actually learn from existing skills and official docs — not just read them.

## Phase 1: Discover Existing Skills

### Search
1. Fetch registries listed in [skill-sources.md](./skill-sources.md)
2. Search for target domain keywords (e.g., "Swift", "React", "deployment")
3. If matches found → `repomix` the top 1–2 most relevant repos

### Extract

For each discovered skill, create an **extraction note** with these sections:

**Structure patterns:**
- How is SKILL.md organized? (sections, headings, flow)
- How are references split? (by feature? by concept? by workflow?)
- What progressive disclosure pattern is used?
- What line counts work well for their content density?

**Content worth reusing:**
- Code patterns that match our project's stack and are correct
- Decision trees, checklists, or flowcharts
- Anti-patterns / pitfalls lists (high-value, hard to generate from scratch)
- Anything project-agnostic and technically accurate

**Content to skip:**
- Project-specific conventions that don't apply
- Outdated APIs or deprecated patterns
- Topics irrelevant to our project's domain
- Overly generic advice ("write clean code")

**Gaps identified:**
- What does our project need that this skill doesn't cover?
- What does this skill get wrong or oversimplify for our context?
- What APIs or patterns are missing entirely?

### Gate — REQUIRED before proceeding

Articulate explicitly:

> "From [skill-name] I will reuse: [list specific items].
> I will skip: [list specific items and why].
> Gaps to fill from other sources: [list]."

If nothing is reusable, state that explicitly:

> "Reviewed [skill-name]. Nothing applicable — it covers [X] but we need [Y]."

**DO NOT** proceed to Phase 2 without this gate. Reading a skill and moving on without articulating what was learned is wasted work.

## Phase 2: Fetch Official Docs

### Use docs-seeker, not raw web searches

Activate the `/docs-seeker` skill with the target technology. This fetches structured, authoritative documentation — not blog posts or Stack Overflow answers.

Raw `WebSearch` is a fallback for topics where docs-seeker finds nothing, not the default.

### What to extract from docs
- API signatures and correct usage patterns
- Recommended patterns from the vendor (Apple, Google, etc.)
- Migration guides (old API → new API) — critical for avoiding deprecated patterns
- Performance recommendations and known limitations
- Concurrency / threading requirements

### Gate — REQUIRED before proceeding

List concretely:
- Which doc sources were fetched (URLs or doc names)
- What patterns were extracted from each
- What was NOT found and needs model knowledge as fallback

## Phase 3: Synthesize

Combine all sources into skill content:

| Source | What it provides | Use for |
|--------|-----------------|---------|
| Existing skills | Proven structure, organization, battle-tested patterns | Skill layout, reference splitting, anti-patterns |
| Official docs | Accuracy, API correctness, vendor recommendations | Code examples, API usage, correct signatures |
| Project codebase | Real examples, actual conventions in use | Grounding examples in what the project actually does |
| Model knowledge | Gap-filling where sources had nothing | Flag explicitly — lower confidence than sourced content |

### Synthesis checklist

- [ ] Every code example is verified against official docs (not just model recall)
- [ ] No verbatim copy-paste from existing skills — adapt to project context
- [ ] All gaps identified in Phase 1 are addressed
- [ ] Content sourced from model knowledge (no doc backing) is flagged
- [ ] Existing skill structure patterns are consciously adopted or rejected (not ignored)

## Anti-patterns

These are real failure modes observed in practice:

| Anti-pattern | What happens | Fix |
|-------------|-------------|-----|
| **Read and forget** | Read an existing skill, say "thorough understanding", write entirely from model knowledge | Use the extraction gate — articulate reuse/skip/gaps |
| **Generic web search** | 2 broad WebSearch queries instead of docs-seeker | Use `/docs-seeker` first, WebSearch only as fallback |
| **Vague synthesis claim** | "I combined existing patterns with official docs" without evidence | List what was combined from where |
| **Research for ceremony** | Follow the research steps because told to, extract nothing, produce same output as without research | If research yields nothing useful, say so and skip — don't waste tool calls |
| **Scope mismatch** | Existing skill covers different domain (SwiftUI nav vs AVFoundation), read it anyway, learn nothing | Check skill scope BEFORE deep-reading — skim SKILL.md first, only read references if relevant |

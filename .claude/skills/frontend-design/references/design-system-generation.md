# Design System Generation Workflow

When generating a complete design system recommendation for a project, follow this multi-domain search orchestration.

## Workflow

### Step 1: Identify Product Category

```bash
python3 .claude/skills/frontend-design/scripts/search.py "user query" --domain products --top 1 --json
```

Extract `Product Type` from the result — this is the category (e.g., "SaaS", "E-Commerce", "FinTech").

### Step 2: Get Reasoning Rules

```bash
python3 .claude/skills/frontend-design/scripts/search.py "category from step 1" --domain ui-reasoning --top 1 --json
```

Extract from the result:
- `Style_Priority` — which styles to prioritize (e.g., "Glassmorphism + Flat Design")
- `Color_Mood` — color direction (e.g., "Trust blue + Accent contrast")
- `Typography_Mood` — font mood (e.g., "Professional + Hierarchy")
- `Key_Effects` — animation/effect guidelines
- `Anti_Patterns` — what to avoid
- `Decision_Rules` — conditional logic (JSON)

### Step 3: Multi-Domain Search

Run these searches independently, or in parallel when your environment supports it.
Use the style priority from Step 2 to weight the style search.

```bash
# Style — weighted by reasoning's Style_Priority
python3 .claude/skills/frontend-design/scripts/search.py "user query + style priority keywords" --domain styles --top 3 --json

# Colors — match product type
python3 .claude/skills/frontend-design/scripts/search.py "user query" --domain colors --top 2 --json

# Landing patterns
python3 .claude/skills/frontend-design/scripts/search.py "user query" --domain landing --top 2 --json

# Typography
python3 .claude/skills/frontend-design/scripts/search.py "user query" --domain typography --top 2 --json
```

### Step 4: Aggregate Best Matches

From the parallel search results, select:

| Domain | Selection Strategy |
|--------|--------------------|
| **Style** | Pick the result whose `Style Category` best matches the reasoning's `Style_Priority`. If multiple priorities (e.g., "Glassmorphism + Flat Design"), prefer the first. |
| **Colors** | Pick the top result matching the product type. |
| **Landing** | Pick the top result. Use `Section Order`, `Primary CTA Placement`, `Color Strategy`. |
| **Typography** | Pick the top result. Use `Heading Font`, `Body Font`, `Google Fonts URL`, `CSS Import`. |

### Step 5: Present Design System

Combine everything into a cohesive recommendation:

**Pattern**
- Name, section order, CTA placement from landing results
- Conversion strategy from landing's `Conversion Optimization`

**Style**
- Style name, keywords, effects from style results
- Performance and accessibility notes

**Colors**
- Primary, On Primary, Secondary, On Secondary, Accent, On Accent, Background, Foreground, and Border values from color results
- Use the paired "on" colors to preserve readable text and UI contrast on each surface

**Typography**
- Heading + Body font pairing
- Google Fonts URL and CSS Import for easy integration
- Mood keywords for context

**Effects & Animation**
- Combine style's `Effects & Animation` with reasoning's `Key_Effects`

**Anti-Patterns (what to avoid)**
- From reasoning's `Anti_Patterns`
- Always include: no emoji icons, cursor-pointer required, 4.5:1 contrast minimum

**Decision Rules (conditional guidance)**
- From reasoning's `Decision_Rules` JSON — present as "if X, then Y" guidance

## Example

Query: "SaaS analytics dashboard"

1. Products search → Category: "SaaS (General)"
2. Reasoning search → Style Priority: "Glassmorphism + Flat Design", Anti-patterns: "Excessive animation + Dark mode by default"
3. Parallel searches → Style: Glassmorphism, Colors: SaaS palette, Landing: SaaS Starter pattern, Typography: Professional pairing
4. Present unified recommendation with all sections above

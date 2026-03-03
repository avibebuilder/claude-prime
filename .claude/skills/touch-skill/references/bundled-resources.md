# Bundled Resources

## Overview

Resources extend SKILL.md without bloating context. Each type serves different purpose.

## scripts/

**Purpose:** Executable code for deterministic, repeatable tasks.

**When to include:**
- Same code rewritten repeatedly
- Deterministic reliability needed
- Complex operations (PDF manipulation, API calls)

**Benefits:**
- Token efficient (execute without loading context)
- Deterministic results
- Testable and versioned

**Examples:**
- `scripts/rotate_pdf.py` - PDF rotation
- `scripts/fetch_data.py` - API fetching
- `scripts/validate.py` - Data validation

**Requirements:**
- Write tests (`scripts/tests/`)
- Run tests until passing
- Manual verification with real use cases
- Respect .env hierarchy

## references/

**Purpose:** Documentation loaded on-demand into context.

**When to include:**
- Detailed guides too long for SKILL.md
- API documentation
- Database schemas
- Domain knowledge, policies

**Benefits:**
- Keeps SKILL.md lean
- Loaded only when needed
- Progressive disclosure

**Examples:**
- `references/api_docs.md` - API specifications
- `references/schema.md` - Database schemas
- `references/patterns.md` - Common patterns

**Best practice:** If file >10k words, include grep patterns in SKILL.md.

## workflows/

**Purpose:** Step-by-step procedures for specific scenarios.

**When to include:**
- Multi-step processes
- Different paths for different inputs
- Decision trees

**Examples:**
- `workflows/new-skill.md` - Creating from scratch
- `workflows/topic-search.md` - Fast documentation lookup
- `workflows/refactor-skill.md` - Improving existing skills

## assets/

**Purpose:** Files used in output, NOT loaded into context.

**When to include:**
- Templates copied to output
- Images, icons, fonts
- Boilerplate code directories

**Examples:**
- `assets/logo.png` - Brand assets
- `assets/template.pptx` - PowerPoint templates
- `assets/starter/` - Boilerplate project

**Benefits:**
- Separates output resources from documentation
- Zero context overhead

## Avoid Duplication

Information lives in ONE place:
- SKILL.md: Essential workflow, navigation
- references/: Detailed documentation
- workflows/: Step-by-step procedures

Never duplicate between files.

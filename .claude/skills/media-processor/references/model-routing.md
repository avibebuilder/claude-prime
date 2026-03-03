# Model Routing

Task-based model selection for ai-multimodal. Model IDs change frequently — check the [official models page](https://ai.google.dev/gemini-api/docs/models) for latest.

## Default Routing

| Task | Default Model | Rationale |
|------|--------------|-----------|
| `transcribe` | `gemini-3-flash-preview` | Multimodal audio input, cost-effective |
| `analyze` | `gemini-3-flash-preview` | Best cost/quality balance for general analysis |
| `extract` | `gemini-2.5-flash` | Cheapest option, sufficient for document extraction |
| `generate` | `gemini-2.5-flash-image` | Fast image generation (~$0.039/image) — **paid plan required**|
| `generate-hq` | `gemini-3-pro-image-preview` | Nano Banana Pro — 4K output, commercial grade — **paid plan required** |
Override any default with `--model <model-id>`.

## Model Tiers

### Gemini 3 Flash (`gemini-3-flash-preview`)
- Fast, cost-effective multimodal processing
- 1M token context, configurable thinking levels
- ~$0.50-1.00 input / $3.00 output per 1M tokens

### Gemini 2.5 Flash (`gemini-2.5-flash`)
- Stable production workhorse, cheapest option
- 1M token context
- ~$0.30 input / $2.50 output per 1M tokens

### Nano Banana (`gemini-2.5-flash-image`) — **Paid plan required**
- Speed-optimized image generation
- 32.8K token context
- ~$0.039 per generated image

### Nano Banana Pro (`gemini-3-pro-image-preview`) — **Paid plan required**
- Highest-fidelity image generation, 4K output
- Supports 14 reference images, localized edits
- Commercial publishing grade
- Free tier quota is 0 — requires billing enabled on Google AI Studio

## Pricing Reference

See [official pricing page](https://ai.google.dev/gemini-api/docs/pricing) for current rates.

## When to Override

- Complex image analysis: consider `gemini-3.1-pro-preview` over default flash
- Budget-constrained batch jobs: use `gemini-2.5-flash` or `gemini-2.5-flash-lite`
- Production stability: prefer `gemini-2.5-*` (stable) over `gemini-3-*-preview` (preview)

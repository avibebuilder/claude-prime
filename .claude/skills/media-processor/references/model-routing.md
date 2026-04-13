# Model Routing

Task-based model selection for media-processor. Model IDs change frequently — check the [official models page](https://ai.google.dev/gemini-api/docs/models) for latest.

## Default Routing

| Task | Default Model | Rationale |
|------|--------------|-----------|
| `transcribe` | `gemini-3-flash-preview` | Multimodal audio input, best quality/cost balance |
| `analyze` | `gemini-3-flash-preview` | Best quality/cost balance for general analysis |
| `extract` | `gemini-3-flash-preview` | Fast multimodal extraction |
| `generate` | `gemini-3.1-flash-image-preview` | High-efficiency image generation — **paid plan required** |
| `generate-hq` | `gemini-3-pro-image-preview` | 4K output, commercial grade — **paid plan required** |
| document conversion | `gemini-3-flash-preview` | Document-to-markdown via vision |

Override any default with `--model <model-id>`.

## Model Tiers

### Gemini 3.x (Current)

| Model | Best for |
|-------|---------|
| `gemini-3.1-pro-preview` | Complex reasoning, detailed analysis |
| `gemini-3-flash-preview` | General-purpose multimodal, cost-effective |
| `gemini-3.1-flash-lite-preview` | Budget batch jobs, simple tasks |
| `gemini-3.1-flash-image-preview` | Standard image generation |
| `gemini-3-pro-image-preview` | High-quality image gen, 4K, 14 reference images |

### Gemini 2.5 (Legacy — still available)

| Model | Best for |
|-------|---------|
| `gemini-2.5-pro` | Advanced reasoning (if 3.x preview isn't stable enough) |
| `gemini-2.5-flash` | Production stability when preview models aren't suitable |
| `gemini-2.5-flash-lite` | Cheapest option for simple tasks |

## When to Override

- Complex image analysis (dense UI, charts): `--model gemini-3.1-pro-preview`
- Production stability over latest features: `--model gemini-2.5-flash`
- Minimum cost batch jobs: `--model gemini-3.1-flash-lite-preview`


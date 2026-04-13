# API Gotchas & Non-Obvious Details

Things that will cause failures or waste tool calls if you don't know them upfront.

## Image Generation

**`aspect_ratio` must be nested inside `image_config`** — passing it directly to `GenerateContentConfig` raises "Extra inputs are not permitted":

```python
# WRONG
config = types.GenerateContentConfig(
    response_modalities=['image'],
    aspect_ratio='16:9'
)

# CORRECT
config = types.GenerateContentConfig(
    response_modalities=['Image'],  # Capital 'I'
    image_config=types.ImageConfig(
        aspect_ratio='16:9'
    )
)
```

**`response_modalities` requires capital case**: `['Image']`, `['Text']` — not `['image']`, `['text']`.

**Text in images**: max 25 characters, up to 3 phrases.

## Video Processing

**Videos require polling after upload** — they aren't ready immediately:
```python
while myfile.state.name == 'PROCESSING':
    time.sleep(5)
    myfile = client.files.get(name=myfile.name)
```

**Clip to relevant segments** to avoid burning tokens on a full video:
```python
types.Part.from_video_metadata(
    file_uri=myfile.uri,
    start_offset='40s',
    end_offset='80s'
)
```

**FPS control** — lower FPS = fewer tokens. Use `fps=0.5` for presentations, `fps=3-5` for fast action:
```python
types.Part.from_video_metadata(file_uri=myfile.uri, fps=0.5)
```

## Vision / Image Analysis

**Bounding box format**: object detection returns `[ymin, xmin, ymax, xmax]` normalized to `[0, 1000]` — not pixel coordinates. Scale to actual image dimensions.

**Image token formula** (decides whether resizing is worth it):
- Both dimensions ≤ 384px → 258 tokens flat
- Larger → tiled into 768×768 chunks, 258 tokens each
- 1920×1080 = 1,548 tokens. 3840×2160 (4K) = 6,192 tokens.

## Audio

**Token rate**: 32 tokens/second (1 min = 1,920 tokens, 1 hour = 115,200 tokens). Max 9.5 hours per request.

## YouTube

Public videos only. Free tier: 8 hours/day limit.

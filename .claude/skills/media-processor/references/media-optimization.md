# Media Optimization for Gemini API

Quick ffmpeg/ffprobe recipes to prepare oversized media before uploading to Gemini.

## Size Limits

| Method | Limit |
|--------|-------|
| Inline (base64) | 20 MB total request |
| File API | 2 GB per file |

## Video

```bash
# Compress to ~100 MB (two-pass is more accurate, single-pass is fine for most cases)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a aac -b:a 128k -ac 2 output.mp4

# Cap at 1080p (keeps aspect ratio)
ffmpeg -i input.mp4 -vf "scale=1920:-2" -c:v libx264 -crf 23 -c:a aac -b:a 128k output.mp4

# Target specific bitrate (e.g., fit 100 MB in 60s → ~13 Mbps)
ffmpeg -i input.mp4 -c:v libx264 -b:v 13M -c:a aac -b:a 128k output.mp4

# Trim duration (first 60 minutes)
ffmpeg -i input.mp4 -t 3600 -c copy trimmed.mp4

# Split into 1-hour chunks
ffmpeg -i input.mp4 -c copy -segment_time 3600 -f segment chunk_%03d.mp4
```

## Audio

```bash
# Compress to mono AAC (Gemini downsamples to 16kHz mono anyway)
ffmpeg -i input.mp3 -c:a aac -b:a 64k -ar 16000 -ac 1 output.m4a
```

## Images

```bash
# Resize to max 1920px wide (ImageMagick)
convert input.jpg -resize 1920x\> -quality 85 output.jpg

# Or with ffmpeg
ffmpeg -i input.png -vf "scale=1920:-2" output.jpg
```

## Probe File Info

```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

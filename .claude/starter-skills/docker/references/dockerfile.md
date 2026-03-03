# Dockerfile Reference

Efficient Dockerfiles minimize rebuild times through strategic layer ordering, multi-stage builds, and proper caching.

## Multi-Stage Builds

Separate build dependencies from runtime—only artifacts reach the final image.

```dockerfile
FROM node:18 AS builder
COPY package*.json ./
RUN npm ci && npm run build

FROM node:18-slim
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/index.js"]
```

## Layer Caching Strategy

Order instructions least-to-most frequently changed. Docker caches layers based on instruction + content.

```dockerfile
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
```

Changing code only rebuilds final layers—package install is cached.

## COPY vs ADD

Use `COPY` for standard files (predictable, recommended). Use `ADD` only for tar archives or remote URLs.

```dockerfile
COPY ./config /app/
ADD archive.tar.gz /app/
```

## CMD vs ENTRYPOINT

**CMD**: Default command, overridable with `docker run image <cmd>`.
**ENTRYPOINT**: Fixed entry point, combined with CMD for flexible arguments.

```dockerfile
ENTRYPOINT ["python", "app.py"]
CMD ["--config", "default.yaml"]
# docker run image → python app.py --config default.yaml
# docker run image custom.yaml → python app.py custom.yaml
```

## ARG vs ENV

| | Scope | Timing | Use |
|---|-------|--------|-----|
| **ARG** | Build | Build-time | Conditional compilation |
| **ENV** | Image+Runtime | Persisted | Runtime defaults |

```dockerfile
ARG NODE_ENV=production
RUN if [ "$NODE_ENV" = "production" ]; then npm ci --prod; fi

ENV NODE_ENV=production
ENV LOG_LEVEL=info

# docker build --build-arg NODE_ENV=development .
```

## Combining RUN Instructions

Chain commands with `&&` to reduce layers and image size.

```dockerfile
# Inefficient: 3 layers
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# Efficient: 1 layer
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

## Best Practices

- Order layers: stable (dependencies) → dynamic (source code)
- Use multi-stage builds to separate build from runtime
- Chain RUN with `&&` and `\` line continuation
- Prefer `COPY` over `ADD`
- Combine `ENTRYPOINT` + `CMD` for flexible overrides
- Use `ARG` for build-time decisions, `ENV` for runtime
- Place frequently-changing instructions last for cache efficiency

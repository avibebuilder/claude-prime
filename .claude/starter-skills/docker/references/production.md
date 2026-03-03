# Docker Production Configuration

## Healthchecks

HEALTHCHECK instructions monitor container health and enable automatic restart.

```dockerfile
# HTTP-based health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# TCP port check
HEALTHCHECK --interval=10s --timeout=5s CMD nc -z localhost 5432 || exit 1

# Custom command check
HEALTHCHECK --interval=30s CMD /app/check-health.sh || exit 1
```

## Restart Policies

Configure automatic container restart in `docker-compose.yml`:

```yaml
services:
  web:
    restart_policy:
      condition: unless-stopped
      delay: 5s
      max_attempts: 3
```

Options: `no`, `always`, `unless-stopped`, `on-failure`

## Resource Limits

```yaml
services:
  app:
    mem_limit: 512m          # Maximum memory usage
    memswap_limit: 768m      # Max memory + swap
    cpus: '1.5'              # CPU shares
    pids_limit: 200          # Max processes
```

## Logging Configuration

```yaml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: '10m'      # Rotation threshold
        max-file: '3'        # Files to keep
        labels: 'service=api'
```

## Docker Compose Watch (Development)

Enable file synchronization and automatic rebuilds:

```yaml
services:
  web:
    build: .
    watch:
      - action: sync
        path: ./src
        target: /app/src
      - action: rebuild
        path: package.json
```

Run with: `docker compose watch`

## Production vs Development Comparison

| Aspect | Development | Production |
|--------|-------------|------------|
| **Restart** | `no` or `on-failure` | `unless-stopped` |
| **Logging** | Console, all levels | json-file, limited rotation |
| **Resources** | Unlimited | Limits set for stability |
| **Healthchecks** | Optional | Required for orchestration |
| **Watch** | `docker compose watch` | N/A (static images) |
| **Image Tags** | `latest`, dev | Specific versions (semver) |

## Production Checklist

- Define HEALTHCHECK in Dockerfile
- Set appropriate restart policies
- Configure resource limits to prevent memory leaks
- Use json-file logging with rotation
- Pin image versions, never use `latest`
- Run `docker compose up -d` for background services
- Monitor container logs: `docker logs --follow <container>`

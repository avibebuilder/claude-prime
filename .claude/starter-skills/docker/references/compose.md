# Docker Compose Reference

## Service Structure

Minimum viable service: image, ports, restart policy.

```yaml
services:
  web:
    image: nginx:latest
    ports: ["80:80"]
    restart: unless-stopped
```

## Environment Variables

Three methods (highest precedence first):

```yaml
services:
  app:
    environment:
      - OVERRIDE=value          # 1. Inline (wins)
    env_file:
      - .env                    # 2. Default config
      - .env.${ENV:-dev}        # 3. Environment-specific
```

Use `env_file` for non-sensitive config. Docker Secrets for passwords (see security.md).

## Networks

Services only communicate within shared networks.

```yaml
networks:
  frontend:
  backend:
    internal: true              # No external access

services:
  web:
    networks: [frontend]
  api:
    networks: [frontend, backend]
  db:
    networks: [backend]         # Only api can reach db
```

## Volumes

Named (persistent), Bind (dev/config), tmpfs (temporary).

```yaml
volumes:
  db_data:

services:
  postgres:
    volumes:
      - db_data:/var/lib/postgresql/data  # Named
      - ./config:/etc/config:ro            # Bind
```

## Dependencies with Healthchecks

```yaml
services:
  db:
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      retries: 5
  api:
    depends_on:
      db:
        condition: service_healthy  # Waits until db is healthy
```

## Profiles

Conditional services: `docker compose --profile dev up`

```yaml
services:
  debug:
    profiles: [dev]
  monitoring:
    profiles: [prod]
```
## Override Files

Auto-merges `compose.yaml` + `compose.override.yaml`. Explicit: `-f compose.yaml -f compose.prod.yaml`

```yaml
# compose.override.yaml (auto-loaded for dev)
services:
  app:
    volumes: [./src:/app/src]
```

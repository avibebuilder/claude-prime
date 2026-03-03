# Docker Security

## .dockerignore

```
.git
.env*
node_modules
*.md
tests
coverage
.vscode
.idea
```

## Non-Root User (UID > 10000)

```dockerfile
FROM node:18-alpine
RUN addgroup -g 10001 appgroup && \
    adduser -D -u 10001 -G appgroup appuser
WORKDIR /app
COPY --chown=appuser:appgroup . .
USER appuser
CMD ["node", "index.js"]
```

## Secrets Management

```yaml
services:
  app:
    secrets:
      - db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

Access: Read from `/run/secrets/db_password`

## Vulnerability Scanning

```bash
# Trivy
trivy image myapp:latest
trivy image --severity HIGH,CRITICAL myapp:latest

# Docker Scout
docker scout cves myapp:latest
```

## Network Isolation

```yaml
networks:
  frontend:
  backend:

services:
  web:
    networks: [frontend]
  api:
    networks: [frontend, backend]
  db:
    networks: [backend]
```

## Read-Only Filesystem

```yaml
services:
  app:
    read_only: true
    tmpfs: [/tmp, /var/run]
```

## Runtime Hardening

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    cap_drop: [ALL]
    cap_add: [NET_BIND_SERVICE]  # Only if needed
```

## Image Signing

```bash
docker pull --disable-content-trust=false myregistry/myapp:latest
docker trust inspect --pretty myapp:latest
```

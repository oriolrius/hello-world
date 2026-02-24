# Docker

Container configuration for the hello-world application.

## Quick Start

```bash
# Run from GitHub Container Registry
docker compose up -d

# Or build locally
docker build -t hello-world -f docker/Dockerfile .
docker run -p 49000:49000 hello-world
```

## Files

| File | Description |
|------|-------------|
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Container orchestration configuration |
| `.dockerignore` | Build context exclusions |

## Dockerfile

Multi-stage build using Python 3.13 slim base image with `uv` for fast dependency installation.

### Build Stages

```
python:3.13-slim → Install uv → Copy source → Install app → Run
```

### Image Details

| Attribute | Value |
|-----------|-------|
| Base Image | `python:3.13-slim` |
| Package Manager | `uv` (copied from `ghcr.io/astral-sh/uv:latest`) |
| Working Directory | `/app` |
| Exposed Port | `49000` |
| Entry Point | `hello-world --bind 0.0.0.0 --port 49000` |

### OCI Labels

| Label | Value |
|-------|-------|
| `org.opencontainers.image.source` | https://github.com/oriolrius/hello-world |
| `org.opencontainers.image.description` | Simple hello-world web server |
| `org.opencontainers.image.licenses` | MIT |

### Build Locally

```bash
# From repository root
docker build -t hello-world -f docker/Dockerfile .

# Run
docker run -p 49000:49000 hello-world

# Test
curl http://localhost:49000
```

## Docker Compose

Production-ready configuration for deploying the containerized application.

### Service Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| Image | `ghcr.io/oriolrius/hello-world:v4` | Pre-built image from GHCR |
| Ports | `49000:49000` | Host:Container port mapping |
| Restart | `unless-stopped` | Auto-restart on failure or reboot |

### Health Check

| Parameter | Value | Description |
|-----------|-------|-------------|
| Test | `curl -f http://localhost:49000/` | HTTP health probe |
| Interval | `30s` | Time between checks |
| Timeout | `10s` | Max time for health check |
| Retries | `3` | Failures before unhealthy |
| Start Period | `5s` | Grace period on startup |

### Usage

```bash
cd docker/

# Start in background
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps

# Stop
docker compose down
```

### Update to New Version

```bash
cd docker/

# Pull latest image
docker compose pull

# Recreate container
docker compose up -d
```

### Use Specific Version

Edit `docker-compose.yml` to change the image tag:

```yaml
services:
  hello-world:
    image: ghcr.io/oriolrius/hello-world:v4.3.3  # specific version
```

Available tag formats:
- `v4` - Latest v4.x release (rolling)
- `v4.3` - Latest v4.3.x release (rolling)
- `v4.3.3` - Exact version (immutable)

## Container Registry

Images are published to GitHub Container Registry on each release.

### Pull Image

```bash
docker pull ghcr.io/oriolrius/hello-world:v4
```

### Available Tags

| Tag Pattern | Example | Description |
|-------------|---------|-------------|
| `v{major}` | `v4` | Latest major version |
| `v{major}.{minor}` | `v4.3` | Latest minor version |
| `v{major}.{minor}.{patch}` | `v4.3.3` | Exact version |

## Architecture

See [../README.md](../README.md) for the full architecture overview including CI/CD pipeline and AWS deployment.

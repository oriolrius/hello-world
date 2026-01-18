# CI/CD Pipeline Architecture

This document describes the GitHub Actions CI/CD pipeline for the hello-world application.

## Architecture Diagram

![CI/CD Pipeline](cicd-architecture.png)

> Editable version: [cicd-architecture.drawio.png](cicd-architecture.drawio.png) (open with [draw.io](https://app.diagrams.net/))

### Connection Color Legend

| Color | Line Style | Meaning |
|-------|------------|---------|
| **Blue** | Solid | Git operations (push, trigger) |
| **Purple** | Solid/Dashed | CI/CD pipeline flow |
| **Orange** | Solid/Dashed | Container image operations |
| **Green** | Solid/Dashed | Deployment and user traffic |
| **Gray** | Dotted | Kubernetes internal communication |

## Overview

The pipeline is defined in `release.yml` and automates the complete software delivery lifecycle:

1. **Quality Gates** - Lint and test the code
2. **Build & Release** - Create GitHub release and Docker image
3. **Deploy** - Deploy to AWS EKS cluster

## Trigger Events

| Event | Description |
|-------|-------------|
| `push tags: v*` | Any tag starting with `v` (e.g., `v1.0.0`, `v2.1.3`) |
| `workflow_dispatch` | Manual trigger from GitHub Actions UI |

## Pipeline Stages

### Stage 1: Quality Gates (Parallel)

Two jobs run in parallel to validate code quality:

#### Lint Job

```yaml
- uses: astral-sh/setup-uv@v4
- run: uv sync --dev
- run: uv run ruff check src/ tests/
- run: uv run ruff format --check src/ tests/
```

- **Purpose**: Code style and quality checks
- **Tool**: [Ruff](https://docs.astral.sh/ruff/) - Fast Python linter
- **Checks**: Linting rules + format verification

#### Test Job

```yaml
- uses: astral-sh/setup-uv@v4
- run: uv sync --dev
- run: uv run pytest -v
```

- **Purpose**: Run unit tests
- **Tool**: [pytest](https://pytest.org/)
- **Coverage**: All tests in `tests/` directory

### Stage 2: Build & Release (Parallel)

After Stage 1 passes, two jobs run in parallel:

#### Release Job

```yaml
needs: [lint, test]
if: startsWith(github.ref, 'refs/tags/')
- uses: softprops/action-gh-release@v2
  with:
    generate_release_notes: true
```

- **Purpose**: Create GitHub Release
- **Condition**: Only runs for tag pushes
- **Output**: GitHub Release with auto-generated notes

#### Docker Job

```yaml
needs: [lint, test]
- uses: docker/login-action@v3
- uses: docker/metadata-action@v5
- uses: docker/build-push-action@v6
```

- **Purpose**: Build and push Docker image
- **Registry**: `ghcr.io` (GitHub Container Registry)
- **Image**: `ghcr.io/oriolrius/hello-world`

**Image Tags Generated:**

| Tag Pattern | Example | When |
|-------------|---------|------|
| `latest` | `latest` | Tag pushes only |
| `{{version}}` | `1.2.3` | Semantic version |
| `{{major}}.{{minor}}` | `1.2` | Major.minor version |
| `{{sha}}` | `a1b2c3d` | Git commit SHA |

### Stage 3: Deploy

After Docker job completes:

```yaml
needs: [docker]
- uses: aws-actions/configure-aws-credentials@v4
- run: aws eks update-kubeconfig --name esade-teaching
- run: kubectl apply -k k8s/
- run: kubectl rollout status deployment/hello-world
```

- **Purpose**: Deploy to AWS EKS
- **Cluster**: `esade-teaching` in `eu-west-1`
- **Method**: Kustomize (`kubectl apply -k k8s/`)

**Deployment Verification:**

1. Wait for rollout completion (120s timeout)
2. Display pod status
3. Get LoadBalancer URL
4. Send 20 test requests
5. Verify load balancing across pods
6. Fail if < 2 pods reached or > 2 requests failed

## Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `AWS_REGION` | `eu-west-1` | AWS region for EKS |
| `EKS_CLUSTER` | `esade-teaching` | EKS cluster name |
| `REGISTRY` | `ghcr.io` | Container registry |
| `IMAGE_NAME` | `${{ github.repository }}` | Docker image name |

## Required Secrets

| Secret | Purpose |
|--------|---------|
| `GITHUB_TOKEN` | Auto-provided, used for ghcr.io login |
| `AWS_ACCESS_KEY_ID` | AWS credentials for EKS access |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for EKS access |
| `AWS_SESSION_TOKEN` | AWS session token (if using temporary credentials) |

## Job Dependencies

```
┌──────┐     ┌──────┐
│ Lint │     │ Test │
└──┬───┘     └──┬───┘
   │            │
   └─────┬──────┘
         │
    ┌────▼────┐    ┌─────────┐
    │ Docker  │    │ Release │
    └────┬────┘    └─────────┘
         │
    ┌────▼────┐
    │ Deploy  │
    └─────────┘
```

## Permissions

| Job | Permission | Reason |
|-----|------------|--------|
| release | `contents: write` | Create GitHub Release |
| docker | `contents: read` | Read repository |
| docker | `packages: write` | Push to ghcr.io |

## Diagram Source

The architecture diagram was created using [draw.io](https://app.diagrams.net/).

**Base generation (optional):**

```bash
cd tools
source .venv/bin/activate
python generate_workflows_diagram.py
```

This produces a `.dot` file that can be converted to `.drawio` format using `graphviz2drawio`, then manually refined in draw.io.

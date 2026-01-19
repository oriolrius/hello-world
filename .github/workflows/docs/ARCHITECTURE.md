# CI/CD Pipeline Architecture (v3.0.x)

This document describes the GitHub Actions CI/CD pipeline for the hello-world application.

## Architecture Diagram

![CI/CD Pipeline](cicd-architecture.png)

> Editable version: [cicd-architecture.drawio](cicd-architecture.drawio) (open with [draw.io](https://app.diagrams.net/))

### Connection Color Legend

| Color | Line Style | Meaning |
|-------|------------|---------|
| **Blue** | Solid | Git operations (push tag) |
| **Purple** | Solid/Dashed | Release workflow stages |
| **Green** | Solid | Deploy workflow |
| **Gray** | Dotted | CloudFormation provisioning |
| **Orange** | Bold | User HTTP traffic |

## Overview

The CI/CD pipeline consists of two workflows:

1. **release.yml** - Build and release Python package
2. **deploy.yml** - Deploy to AWS via CloudFormation

## Workflows

### release.yml

**Trigger:** Push tags matching `v*` (e.g., `v3.0.0`, `v3.0.1`)

```
Push v* tag → Lint + Test (parallel) → Build → Release
```

#### Jobs

| Job | Depends On | Description |
|-----|------------|-------------|
| `lint` | - | Run ruff check and format verification |
| `test` | - | Run pytest |
| `build` | lint, test | Build wheel with `uv build`, upload artifact |
| `release` | build | Create GitHub Release with dist/* files |

#### Stage 1: Quality Gates (Parallel)

**Lint Job:**
```yaml
- uses: astral-sh/setup-uv@v4
- run: uv sync --dev
- run: uv run ruff check src/ tests/
- run: uv run ruff format --check src/ tests/
```

**Test Job:**
```yaml
- uses: astral-sh/setup-uv@v4
- run: uv sync --dev
- run: uv run pytest -v
```

#### Stage 2: Build

```yaml
needs: [lint, test]
- uses: astral-sh/setup-uv@v4
- run: uv build
- uses: actions/upload-artifact@v4
  with:
    name: dist
    path: dist/
```

#### Stage 3: Release

```yaml
needs: build
permissions:
  contents: write
- uses: actions/download-artifact@v4
- uses: softprops/action-gh-release@v2
  with:
    files: dist/*
```

### deploy.yml

**Triggers:**
- `workflow_dispatch` - Manual trigger
- `release: [published]` - After GitHub Release is published

#### Deploy Job

```yaml
env:
  AWS_REGION: eu-west-1
  STACK_NAME: hello-world

steps:
  - uses: aws-actions/configure-aws-credentials@v4
  - run: aws cloudformation deploy \
      --template-file infra/cloudformation.yml \
      --stack-name hello-world
  - run: aws cloudformation describe-stacks (get outputs)
```

## Job Dependencies

```
release.yml:
┌──────┐     ┌──────┐
│ Lint │     │ Test │
└──┬───┘     └──┬───┘
   │            │
   └─────┬──────┘
         │
    ┌────▼────┐
    │  Build  │
    └────┬────┘
         │
    ┌────▼────┐
    │ Release │
    └────┬────┘
         │
         ▼
deploy.yml:
    ┌────────┐
    │ Deploy │
    └────────┘
```

## Environment Variables

| Variable | Value | Workflow |
|----------|-------|----------|
| `AWS_REGION` | `eu-west-1` | deploy.yml |
| `STACK_NAME` | `hello-world` | deploy.yml |

## Required Secrets

| Secret | Purpose |
|--------|---------|
| `GITHUB_TOKEN` | Auto-provided for release creation |
| `AWS_ACCESS_KEY_ID` | AWS credentials for CloudFormation |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for CloudFormation |
| `AWS_SESSION_TOKEN` | AWS session token (temporary credentials) |

## Permissions

| Job | Permission | Reason |
|-----|------------|--------|
| release | `contents: write` | Create GitHub Release |

## Diagram Source

The architecture diagram was created using [draw.io](https://app.diagrams.net/).

**Base generation (optional):**

```bash
cd tools
source .venv/bin/activate
python generate_workflows_diagram.py
```

This produces a `.dot` file that can be converted to `.drawio` format using `graphviz2drawio`, then manually refined in draw.io.

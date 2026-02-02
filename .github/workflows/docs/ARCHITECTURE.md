# CI/CD Pipeline Architecture (v4-ecr-ecs-fargate)

## Architecture Diagram

![CI/CD Pipeline](cicd-architecture.png)

## Overview

The v4-ecr-ecs-fargate release workflow provides continuous integration with Docker image publishing to Amazon ECR. Deployment to ECS Fargate is manual via Makefile.

## Pipeline Flow

```
          ┌─────┐     ┌──────┐
          │lint │     │ test │
          └──┬──┘     └──┬───┘
             │           │
     ┌───────┴───────────┴───────┐
     │                           │
     ▼                           ▼
┌─────────┐                 ┌─────────┐
│  build  │                 │ docker  │
└────┬────┘                 └─────────┘
     │                           │
     ▼                           ▼
┌─────────┐                 ┌─────────┐
│ release │                 │   ECR   │
└─────────┘                 └─────────┘
                                 │
                                 ▼ (manual)
                            ┌─────────┐
                            │   ECS   │
                            │ Fargate │
                            └─────────┘
```

## Jobs

### lint

Runs code quality checks using ruff.

```yaml
- run: uv run ruff check src/ tests/
- run: uv run ruff format --check src/ tests/
```

### test

Executes the test suite with pytest.

```yaml
- run: uv run pytest -v
```

### build

Builds Python wheel and source distributions.

```yaml
- run: uv build
- uses: actions/upload-artifact@v4
```

**Depends on:** lint, test

### release

Creates GitHub Release with wheel artifacts.

```yaml
- uses: softprops/action-gh-release@v2
  with:
    files: dist/*
```

**Depends on:** build

### docker

Builds and pushes Docker image to Amazon ECR.

```yaml
- uses: aws-actions/amazon-ecr-login@v2
- uses: docker/build-push-action@v6
  with:
    context: .
    file: docker/Dockerfile
    push: true
```

**Image tags** (all with `-ecr-ecs-fargate` suffix):
- `v{version}-ecr-ecs-fargate` (e.g., v4.4.0-ecr-ecs-fargate)
- `v{major}.{minor}-ecr-ecs-fargate` (e.g., v4.4-ecr-ecs-fargate)
- `v{major}-ecr-ecs-fargate` (e.g., v4-ecr-ecs-fargate)
- `sha-{sha}-ecr-ecs-fargate` (e.g., sha-abc1234-ecr-ecs-fargate)

**Depends on:** lint, test

## Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `AWS_REGION` | eu-west-1 | AWS region |
| `STACK_NAME` | hello-world-ecr-ecs-fargate | CloudFormation stack name |

## Required Secrets

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS access key for ECR |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_SESSION_TOKEN` | AWS session token (if using temporary credentials) |

## Manual Deployment

Deployment is not automated. After the CI pushes to ECR:

```bash
# Force new ECS deployment with the pushed image
make redeploy

# Or deploy with a specific tag
make deploy TAG=v4.4.0-ecr-ecs-fargate

# Check status
make status
```

## Trigger

The workflow triggers on:
- Push of tags matching `v*-ecr-ecs-fargate`
- Manual trigger via `workflow_dispatch`

## Diagram Source

The diagram is generated from `tools/generate_workflows_diagram.py`:

```bash
cd tools
source .venv/bin/activate
python generate_workflows_diagram.py
```

Editable version: [cicd-architecture.drawio](cicd-architecture.drawio)

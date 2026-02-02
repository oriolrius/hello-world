# GitHub Workflows

## Quick Reference

| Workflow | Trigger | Description |
|----------|---------|-------------|
| [release.yml](release.yml) | `push tag v*-ecr-ecs-fargate`, `workflow_dispatch` | CI pipeline (lint, test, build, push to ECR) |

## How to Trigger a Release

```bash
# Using commitizen (recommended)
cz bump

# Or manually create and push a version tag
git tag v4.4.0-ecr-ecs-fargate
git push origin v4.4.0-ecr-ecs-fargate
```

Or manually via GitHub Actions UI using `workflow_dispatch`.

## Files

| File | Description |
|------|-------------|
| `release.yml` | Main CI workflow |
| `docs/` | Architecture documentation and diagrams |

## Required Secrets

Configure these in repository Settings > Secrets > Actions:

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key |
| `AWS_SESSION_TOKEN` | Optional | For temporary credentials |

## Deployment

Deployment to ECS Fargate is **manual** (not automated in CI). Use the Makefile:

```bash
# Push image to ECR
make ecr-push TAG=v4.4.0-ecr-ecs-fargate

# Force new ECS deployment
make redeploy

# Check status
make status
```

See [infra/docs/ARCHITECTURE.md](/infra/docs/ARCHITECTURE.md) for infrastructure details.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed pipeline documentation.

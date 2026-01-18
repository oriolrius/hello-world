# GitHub Actions Workflows

This folder contains the CI/CD pipeline definitions for the hello-world application.

## Workflows

| Workflow | File | Trigger | Description |
|----------|------|---------|-------------|
| Release | [release.yml](release.yml) | `v*` tags, manual | Full CI/CD pipeline: lint, test, build, deploy |

## Quick Reference

### Triggering a Release

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### Manual Trigger

1. Go to **Actions** tab in GitHub
2. Select **Release** workflow
3. Click **Run workflow**

## Pipeline Overview

```
Push v* tag → Lint + Test → Docker Build → Deploy to EKS
                         → GitHub Release
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## Files

| File | Purpose |
|------|---------|
| `release.yml` | Main CI/CD pipeline definition |
| `ARCHITECTURE.md` | Detailed pipeline documentation |
| `cicd-architecture.png` | Pipeline architecture diagram |
| `cicd-architecture.drawio.png` | Editable diagram source |
| `cicd-architecture.dot` | GraphViz source (auto-generated) |

## Required Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key for EKS deployment |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key for EKS deployment |
| `AWS_SESSION_TOKEN` | Optional | AWS session token (temporary credentials) |

> **Note:** `GITHUB_TOKEN` is automatically provided by GitHub Actions.

## Related Documentation

- [Kubernetes Manifests](../../k8s/README.md)
- [Infrastructure Architecture](../../infra/ARCHITECTURE.md)
- [Docker Configuration](../../docker/README.md)

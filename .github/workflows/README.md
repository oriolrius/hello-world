# GitHub Actions Workflows

This folder contains the CI/CD pipeline definitions for the hello-world application.

## Workflows

| Workflow | File | Trigger | Description |
|----------|------|---------|-------------|
| Release | [release.yml](release.yml) | `v*` tags | Lint, test, build, and create GitHub Release |
| Deploy | [deploy.yml](deploy.yml) | Release published, manual | Deploy to AWS via CloudFormation |

## Quick Reference

### Triggering a Release

```bash
# Create and push a version tag
git tag v3.0.2
git push origin v3.0.2
```

This triggers:
1. **release.yml** → Builds and creates GitHub Release
2. **deploy.yml** → Automatically deploys after release is published

### Manual Deploy

1. Go to **Actions** tab in GitHub
2. Select **Deploy** workflow
3. Click **Run workflow**

## Pipeline Overview

```
Push v* tag → Lint + Test → Build → GitHub Release → CloudFormation Deploy
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

## Files

| File | Purpose |
|------|---------|
| `release.yml` | Build and release pipeline |
| `deploy.yml` | CloudFormation deployment |
| `docs/ARCHITECTURE.md` | Detailed pipeline documentation |
| `docs/cicd-architecture.png` | Pipeline architecture diagram |
| `docs/cicd-architecture.drawio` | Editable diagram source |
| `docs/cicd-architecture.dot` | GraphViz source (auto-generated) |

## Required Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key for CloudFormation |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key for CloudFormation |
| `AWS_SESSION_TOKEN` | Optional | AWS session token (temporary credentials) |

> **Note:** `GITHUB_TOKEN` is automatically provided by GitHub Actions.

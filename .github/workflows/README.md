# GitHub Workflows

## Quick Reference

| Workflow | Trigger | Description |
|----------|---------|-------------|
| [release.yml](release.yml) | `push tag v*`, `workflow_dispatch` | Full CI/CD pipeline |

## How to Trigger a Release

```bash
# Create and push a version tag
git tag v4.3.4
git push origin v4.3.4
```

Or manually via GitHub Actions UI using `workflow_dispatch`.

## Files

| File | Description |
|------|-------------|
| `release.yml` | Main CI/CD workflow |
| `docs/` | Architecture documentation and diagrams |

## Required Secrets

Configure these in repository Settings → Secrets → Actions:

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key |
| `AWS_SESSION_TOKEN` | Optional | For temporary credentials |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed pipeline documentation.

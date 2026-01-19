# GitHub Workflows - v4.0.x

This folder contains the CI/CD workflows for the hello-world application.

## Quick Reference

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `release.yml` | Tag push (`v*`) | Lint, test, build, create GitHub release |
| `deploy.yml` | Release published / Manual | Deploy to AWS with CloudFormation + Ansible |

## How to Trigger a Release

1. Create and push a version tag:
   ```bash
   git tag -a v4.0.1 -m "Release v4.0.1"
   git push origin v4.0.1
   ```

2. The release workflow will:
   - Run linting and tests
   - Build the Python package
   - Create a GitHub release with artifacts

3. The deploy workflow will automatically trigger when the release is published

## Manual Deployment

To deploy without creating a release:

1. Go to **Actions** → **Deploy** → **Run workflow**
2. Select the branch and click **Run workflow**

## Files

| File | Description |
|------|-------------|
| `release.yml` | Release workflow with lint, test, build jobs |
| `deploy.yml` | Deployment workflow with CloudFormation and Ansible |
| `docs/ARCHITECTURE.md` | Detailed architecture documentation |
| `docs/cicd-architecture.png` | Architecture diagram |
| `docs/cicd-architecture.dot` | Graphviz source for diagram |
| `docs/cicd-architecture.drawio` | Editable diagram (draw.io format) |

## Required Secrets

Configure these secrets in your repository settings:

- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_SESSION_TOKEN` - AWS session token (optional, for temporary credentials)
- `EC2_SSH_KEY` - SSH private key for EC2 access

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

![CI/CD Architecture](docs/cicd-architecture.png)

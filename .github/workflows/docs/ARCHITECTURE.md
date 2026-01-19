# CI/CD Pipeline Architecture - v4.0.x

This document describes the CI/CD pipeline architecture for the hello-world application version 4.0.x.

## Architecture Diagram

![CI/CD Pipeline Architecture](cicd-architecture.png)

## Connection Color Legend

| Color  | Description                           |
|--------|---------------------------------------|
| Blue   | Release workflow (tag push → release) |
| Green  | Deploy workflow (release → EC2)       |
| Orange | Deployment action (Ansible → EC2)     |

## Overview

The CI/CD pipeline consists of two GitHub Actions workflows:

1. **Release Workflow** (`release.yml`) - Triggered by tag pushes, handles quality checks and creates GitHub releases
2. **Deploy Workflow** (`deploy.yml`) - Triggered by releases or manual dispatch, deploys infrastructure and application

## Release Workflow

The release workflow runs when a version tag (e.g., `v4.0.1`) is pushed.

### Jobs

#### 1. Lint Job

Runs code quality checks using ruff:

```yaml
- run: uv run ruff check src/ tests/
- run: uv run ruff format --check src/ tests/
```

#### 2. Test Job

Runs the test suite:

```yaml
- run: uv run pytest -v
```

#### 3. Build Job

Builds the Python package (runs after lint and test pass):

```yaml
needs: [lint, test]
- run: uv build
```

#### 4. Release Job

Creates a GitHub release with build artifacts:

```yaml
needs: build
- uses: softprops/action-gh-release@v2
```

### Job Dependencies

```
     ┌──────┐     ┌──────┐
     │ Lint │     │ Test │
     └───┬──┘     └───┬──┘
         │           │
         └─────┬─────┘
               │
         ┌─────▼─────┐
         │   Build   │
         └─────┬─────┘
               │
         ┌─────▼─────┐
         │  Release  │
         └───────────┘
```

## Deploy Workflow

The deploy workflow handles infrastructure provisioning and application deployment.

### Triggers

- **Release Published**: Automatically deploys when a GitHub release is published
- **Manual Dispatch**: Can be triggered manually from the GitHub Actions UI

### Steps

1. **Configure AWS Credentials** - Sets up AWS authentication
2. **Create/Use Key Pair** - Manages SSH key for EC2 access
3. **Deploy CloudFormation** - Creates/updates AWS infrastructure
4. **Wait for EC2** - Waits until the instance is ready
5. **Get EC2 IP** - Retrieves the public IP address
6. **Create Ansible Inventory** - Generates inventory file
7. **Deploy with Ansible** - Runs the Ansible playbook
8. **Verify Deployment** - Tests the deployed service

### Deployment Flow

```
┌────────────────┐
│ Release Event  │
│  or Manual     │
└───────┬────────┘
        │
┌───────▼────────┐
│ CloudFormation │
│    Deploy      │
└───────┬────────┘
        │
┌───────▼────────┐
│ Wait for EC2   │
│   Instance     │
└───────┬────────┘
        │
┌───────▼────────┐
│    Ansible     │
│   Playbook     │
└───────┬────────┘
        │
┌───────▼────────┐
│    Verify      │
│  Deployment    │
└────────────────┘
```

## Environment Variables

| Variable    | Value       | Description              |
|-------------|-------------|--------------------------|
| AWS_REGION  | eu-west-1   | AWS region for deployment|
| STACK_NAME  | hello-world | CloudFormation stack name|
| KEY_NAME    | hello-world-deploy-key | EC2 key pair name |

## Required Secrets

| Secret               | Description                          |
|----------------------|--------------------------------------|
| AWS_ACCESS_KEY_ID    | AWS access key for authentication    |
| AWS_SECRET_ACCESS_KEY| AWS secret key for authentication    |
| AWS_SESSION_TOKEN    | AWS session token (if using STS)     |
| EC2_SSH_KEY          | Private SSH key for EC2 access       |

## Diagram Source

The architecture diagram is generated using the [diagrams](https://diagrams.mingrammer.com/) library.

To regenerate the diagram:

```bash
cd tools
source .venv/bin/activate
python generate_workflows_diagram.py
```

The editable `.drawio` file is also available for manual adjustments.

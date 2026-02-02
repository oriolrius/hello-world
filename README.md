# hello-world

A teaching project that demonstrates the evolution of DevOps practices. The application itself is intentionally trivial — a web server that returns "hello-world" — because the focus is on **how software is built, tested, and delivered**, not the application logic.

## What This Version Demonstrates (v4.x)

This version introduces **Containerization** with Docker and **Infrastructure as Code** with CloudFormation UserData:

| Practice                | Implementation                         |
| ----------------------- | -------------------------------------- |
| Containerization        | Docker image with multi-stage build    |
| Container Registry      | GitHub Container Registry (ghcr.io)    |
| Container Orchestration | Docker Compose for deployment          |
| Infrastructure          | AWS CloudFormation with UserData       |
| Configuration           | Cloud-init bootstraps Docker on boot   |

### Single-Step Deployment

Unlike previous versions that required separate infrastructure and configuration steps, v4.x uses **CloudFormation UserData** to bootstrap the entire stack:

```
CloudFormation → EC2 UserData → Install Docker → Pull image → Run container
```

### Architecture Overview

![Architecture Overview](infra/docs/infra-architecture.png)

### Key Features

| Aspect       | Implementation                                     |
| ------------ | -------------------------------------------------- |
| Runtime      | Container                                          |
| Dependencies | Bundled in image                                   |
| Isolation    | Fully isolated                                     |
| Portability  | Any Docker host                                    |
| Updates      | Pull new image                                     |
| Rollback     | `docker compose down && up` with old tag           |

### Why Docker?

1. **Immutable artifacts**: The image is the same everywhere (dev, staging, prod)
2. **Isolation**: App doesn't pollute or depend on host system
3. **Portability**: Runs anywhere Docker runs (cloud, local, CI)
4. **Version pinning**: `image:v4.0.0` guarantees exact version

**Key learning**: Containers decouple the application from the host, making deployments reproducible and rollbacks trivial.

## Installation

```bash
uv sync
```

## Usage

### Development mode

```bash
uv run hello-world
```

### From virtual environment

```bash
.venv/bin/hello-world
```

### With uvx (no install)

```bash
uvx --from git+https://github.com/oriolrius/hello-world hello-world
```

### From wheel

```bash
uv build
uvx --from ./dist/hello_world-*.whl hello-world
```

## Development

```bash
uv run ruff check src/ tests/   # lint
uv run ruff format src/ tests/  # format
uv run pytest -v                # test
uv build                        # build .tar.gz and .whl
```

## Parameters

| Flag           | Description  | Default     |
| -------------- | ------------ | ----------- |
| `-b, --bind` | Bind address | `0.0.0.0` |
| `-p, --port` | Port number  | `49000`   |

## Examples

```bash
hello-world                        # http://0.0.0.0:49000
hello-world -p 8080                # http://0.0.0.0:8080
hello-world -b 127.0.0.1 -p 3000   # http://127.0.0.1:3000
```

## AWS Deployment

Deployment is a **single-step process** using CloudFormation with UserData:

**CloudFormation** → Provisions infrastructure AND configures the instance (installs Docker, deploys the container)

### Quick Start

```bash
# Step 1: Deploy infrastructure with CloudFormation
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1

# Step 2: Get the EC2 public IP
IP=$(aws cloudformation describe-stacks \
  --stack-name hello-world \
  --region eu-west-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
  --output text)

# Step 3: Test the deployment (wait ~2 min for UserData to complete)
curl http://$IP:49000
```

### What CloudFormation Creates

The CloudFormation template (`infra/cloudformation.yml`) creates:

| Resource         | Description                    |
| ---------------- | ------------------------------ |
| VPC              | 10.0.0.0/16 with DNS support   |
| Subnet           | Public subnet 10.0.1.0/24      |
| Internet Gateway | For public internet access     |
| Security Group   | Ports 22 (SSH) and 49000 (app) |
| EC2 Instance     | t3a.micro with Ubuntu 24.04 LTS |

### What UserData Installs

The EC2 UserData script automatically:

| Task                   | Description                              |
| ---------------------- | ---------------------------------------- |
| Install Docker         | Docker Engine + Compose plugin           |
| Download docker-compose| Fetches from GitHub repository           |
| Start container        | Runs with `docker compose up -d`         |

### CloudFormation Parameters

| Parameter     | Description                 | Default       |
| ------------- | --------------------------- | ------------- |
| `KeyName`   | EC2 Key Pair for SSH access | _(none)_      |
| `AllowedIP` | CIDR for SSH access         | `0.0.0.0/0`   |

### SSH Access (Optional)

To enable SSH, create a key pair and pass it to CloudFormation:

```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name hello-world-key \
  --region eu-west-1 \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/hello-world-key.pem
chmod 600 ~/.ssh/hello-world-key.pem

# Deploy with SSH access
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1 \
  --parameter-overrides KeyName=hello-world-key

# Connect
ssh -i ~/.ssh/hello-world-key.pem ubuntu@$IP
```

### Service Management

```bash
# Check container status
ssh -i ~/.ssh/hello-world-key.pem ubuntu@$IP \
  "sudo docker compose -f /opt/hello-world/docker-compose.yml ps"

# View logs
ssh -i ~/.ssh/hello-world-key.pem ubuntu@$IP \
  "sudo docker compose -f /opt/hello-world/docker-compose.yml logs -f"

# Restart service
ssh -i ~/.ssh/hello-world-key.pem ubuntu@$IP \
  "sudo docker compose -f /opt/hello-world/docker-compose.yml restart"
```

### Cleanup

```bash
aws cloudformation delete-stack \
  --stack-name hello-world \
  --region eu-west-1
```

### GitHub Actions Deployment

The `deploy.yml` workflow runs on release or manual trigger.

**Required secrets:**

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN` _(if using SSO)_

```bash
# Set secrets
gh secret set AWS_ACCESS_KEY_ID --body "your-key"
gh secret set AWS_SECRET_ACCESS_KEY --body "your-secret"

# Trigger manual deployment
gh workflow run deploy.yml
```

# hello-world

A teaching project that demonstrates the evolution of DevOps practices. The application itself is intentionally trivial — a web server that returns "hello-world" — because the focus is on **how software is built, tested, and delivered**, not the application logic.

## What This Version Demonstrates (v4.x)

This version introduces **Containerization** with Docker and **Serverless Container Orchestration** with AWS ECS Fargate:

| Practice                | Implementation                         |
| ----------------------- | -------------------------------------- |
| Containerization        | Docker image with multi-stage build    |
| Container Registry      | Amazon ECR (Elastic Container Registry)|
| Container Orchestration | AWS ECS Fargate (serverless)           |
| Infrastructure          | AWS CloudFormation                     |
| CI/CD                   | GitHub Actions (build, test, push)     |

### Serverless Containers

Unlike traditional EC2-based deployments, ECS Fargate provides **serverless container orchestration**:

```
GitHub Push (tag) → GitHub Actions → Build & Push to ECR → Deploy to ECS Fargate
```

### Architecture Overview

![Architecture Overview](infra/docs/infra-architecture.png)

### Key Features

| Aspect       | Implementation                                     |
| ------------ | -------------------------------------------------- |
| Runtime      | Container on Fargate                               |
| Dependencies | Bundled in image                                   |
| Isolation    | Fully isolated                                     |
| Portability  | Any Docker host / ECS                              |
| Updates      | Push new image, redeploy service                   |
| Rollback     | Deploy previous image tag                          |
| Logging      | CloudWatch Logs                                    |

### Why ECS Fargate?

1. **No servers to manage**: AWS handles the underlying infrastructure
2. **Pay per use**: Only pay for vCPU and memory while tasks run
3. **Automatic scaling**: Scale tasks up/down based on demand
4. **Integrated with ECR**: Native Docker image registry
5. **Built-in logging**: CloudWatch Logs integration

**Key learning**: Serverless containers eliminate infrastructure management while maintaining the benefits of containerization.

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

Deployment is a **two-step process**:

1. **Deploy infrastructure** — CloudFormation creates ECR, ECS cluster, networking, and IAM roles
2. **Push container image** — CI/CD builds and pushes the image to ECR, ECS pulls and runs it

### Quick Start

```bash
# Step 1: Deploy infrastructure (first time only)
make deploy

# Step 2: Build and push Docker image to ECR
make ecr-login
make ecr-push

# Step 3: Get the service public IP
make status

# Step 4: Test the deployment
curl http://<PUBLIC_IP>:49000
```

### What CloudFormation Creates

The CloudFormation template (`infra/cloudformation.yml`) creates:

| Resource            | Description                              |
| ------------------- | ---------------------------------------- |
| ECR Repository      | Container image registry                 |
| VPC                 | 10.0.0.0/16 with DNS support             |
| Subnet              | Public subnet 10.0.1.0/24                |
| Internet Gateway    | For public internet access               |
| Security Group      | Port 49000 (application)                 |
| ECS Cluster         | Fargate cluster                          |
| ECS Task Definition | 0.25 vCPU, 512MB memory                  |
| ECS Service         | Runs 1 task with public IP               |
| CloudWatch Logs     | Application logs (7-day retention)       |
| IAM Role            | Task execution role for ECR/Logs access  |

### CloudFormation Parameters

| Parameter     | Description                     | Default       |
| ------------- | ------------------------------- | ------------- |
| `ImageTag`    | Docker image tag to deploy      | _(required)_  |
| `AllowedIP`   | CIDR for application access     | `0.0.0.0/0`   |

### Makefile Commands

| Command         | Description                              |
| --------------- | ---------------------------------------- |
| `make deploy`   | Deploy CloudFormation stack              |
| `make delete`   | Delete CloudFormation stack              |
| `make ecr-login`| Authenticate Docker to ECR               |
| `make ecr-push` | Build and push image to ECR              |
| `make redeploy` | Force new ECS deployment                 |
| `make status`   | Show service status and public IP        |
| `make logs`     | Tail CloudWatch logs                     |

### View Logs

```bash
# Using Makefile
make logs

# Or manually
aws logs tail /ecs/hello-world-ecr-ecs-fargate --follow
```

### Force Redeployment

After pushing a new image with the same tag:

```bash
make redeploy
```

### Cleanup

```bash
make delete
```

### GitHub Actions Deployment

The `release.yml` workflow runs on tag push (`v*-ecr-ecs-fargate`) or manual trigger.

**Pipeline stages:**
1. **lint** — Ruff check and format validation
2. **test** — pytest execution
3. **build** — Build wheel/sdist, create GitHub release
4. **docker** — Build and push to ECR

**Required secrets:**

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN` _(if using SSO)_

```bash
# Set secrets
gh secret set AWS_ACCESS_KEY_ID --body "your-key"
gh secret set AWS_SECRET_ACCESS_KEY --body "your-secret"

# Create a release tag to trigger deployment
git tag v4.3.3-ecr-ecs-fargate
git push origin v4.3.3-ecr-ecs-fargate
```

## Documentation

| Document | Description |
| -------- | ----------- |
| [CLAUDE.md](CLAUDE.md) | Claude Code instructions and project reference |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines and commit format |
| [infra/README.md](infra/README.md) | Infrastructure deployment details |
| [infra/docs/ARCHITECTURE.md](infra/docs/ARCHITECTURE.md) | Detailed architecture documentation |
| [.github/workflows/README.md](.github/workflows/README.md) | CI/CD workflow documentation |

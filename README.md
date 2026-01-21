# hello-world

A teaching project that demonstrates the evolution of DevOps practices. The application itself is intentionally trivial — a web server that returns "hello-world" — because the focus is on **how software is built, tested, and delivered**, not the application logic.

## What This Version Demonstrates (v5.x)

This version introduces **Containerization** with Docker, packaging the application as a portable container image:

| Practice | Implementation |
|----------|----------------|
| Containerization | Docker image with multi-stage build |
| Container Registry | GitHub Container Registry (ghcr.io) |
| Container Orchestration | Docker Compose for deployment |
| Infrastructure | AWS CloudFormation (unchanged) |
| Configuration Management | Ansible deploys Docker + Compose |

### Evolution from v4.x

- **v4.x**: Ansible installs the app directly on the host using `uv tool install`
- **v5.x**: Ansible installs **Docker**, then deploys the app as a **container**

```
v4.x: Ansible → Install uv → Install app → Run as systemd service
v5.x: Ansible → Install Docker → Pull image → Run as Docker container
```

### Architecture Overview

![Architecture Overview](assets/diagrams/architecture.png)

### Key Differences from v4.x

| Aspect | v4.x (Direct Install) | v5.x (Docker) |
|--------|----------------------|---------------|
| Runtime | Python on host | Container |
| Dependencies | Installed on host | Bundled in image |
| Isolation | Shared with host | Fully isolated |
| Portability | Ubuntu-specific | Any Docker host |
| Updates | Re-run Ansible | Pull new image |
| Rollback | Manual | `docker compose down && up` with old tag |

### Why Docker?

1. **Immutable artifacts**: The image is the same everywhere (dev, staging, prod)
2. **Isolation**: App doesn't pollute or depend on host system
3. **Portability**: Runs anywhere Docker runs (cloud, local, CI)
4. **Version pinning**: `image:v5.0.0` guarantees exact version

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

| Flag | Description | Default |
|------|-------------|---------|
| `-b, --bind` | Bind address | `0.0.0.0` |
| `-p, --port` | Port number | `49000` |

## Examples

```bash
hello-world                        # http://0.0.0.0:49000
hello-world -p 8080                # http://0.0.0.0:8080
hello-world -b 127.0.0.1 -p 3000   # http://127.0.0.1:3000
```

## AWS Deployment

Deployment is a **two-step process**:

1. **CloudFormation** → Provisions AWS infrastructure (VPC, EC2, Security Groups)
2. **Ansible** → Configures the instance (installs Docker, deploys the container)

> **Important**: CloudFormation only creates the infrastructure. You must run the Ansible playbook to deploy the application.

### Quick Start

```bash
# Step 1: Create SSH key pair (one-time setup)
aws ec2 create-key-pair \
  --key-name hello-world-key \
  --region eu-west-1 \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/hello-world-key.pem
chmod 600 ~/.ssh/hello-world-key.pem

# Step 2: Deploy infrastructure with CloudFormation
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1 \
  --parameter-overrides KeyName=hello-world-key

# Step 3: Get the EC2 public IP
IP=$(aws cloudformation describe-stacks \
  --stack-name hello-world \
  --region eu-west-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
  --output text)

# Step 4: Create Ansible inventory
echo "[hello-world]
$IP ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/hello-world-key.pem" > deploy/inventory.ini

# Step 5: Deploy the application with Ansible
uv run ansible-galaxy collection install -r deploy/requirements.yml
cd deploy && uv run ansible-playbook -i inventory.ini playbook.yml

# Step 6: Test the deployment
curl http://$IP:49000
```

### Infrastructure (Step 1-2)

The CloudFormation template (`infra/cloudformation.yml`) creates:

| Resource | Description |
|----------|-------------|
| VPC | 10.0.0.0/16 with DNS support |
| Subnet | Public subnet 10.0.1.0/24 |
| Internet Gateway | For public internet access |
| Security Group | Ports 22 (SSH) and 49000 (app) |
| EC2 Instance | t3.micro with Ubuntu 24.04 LTS |

> **Note**: The EC2 instance is created with a minimal Ubuntu image. Docker and the application are installed by Ansible in the next step.

### Application Deployment (Step 3-5)

The Ansible playbook (`deploy/playbook.yml`) configures the instance:

| Task | Description |
|------|-------------|
| Install Docker | Docker Engine + Compose plugin |
| Deploy container | Pull image from ghcr.io |
| Start service | Run with Docker Compose |

See [`deploy/README.md`](deploy/README.md) for detailed Ansible documentation.

### CloudFormation Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `KeyName` | EC2 Key Pair for SSH access | _(none)_ |
| `AllowedIP` | CIDR for SSH access | `0.0.0.0/0` |

### SSH Access

```bash
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

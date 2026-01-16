# hello-world

Simple web server that returns `hello-world`.

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

Deploy to AWS EC2 using CloudFormation.

### Infrastructure

The CloudFormation template (`infra/cloudformation.yml`) creates:

| Resource | Description |
|----------|-------------|
| VPC | 10.0.0.0/16 with DNS support |
| Subnet | Public subnet 10.0.1.0/24 |
| Internet Gateway | For public internet access |
| Security Group | Ports 22 (SSH) and 49000 (app) |
| EC2 Instance | t3.micro with Ubuntu 24.04 LTS |

The instance runs hello-world as a systemd service on port 49000.

### CloudFormation Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `KeyName` | EC2 Key Pair for SSH access | _(none)_ |
| `AllowedIP` | CIDR for SSH access | `0.0.0.0/0` |

### SSH Access

To enable SSH access, create a key pair first:

```bash
# Create key pair and save private key
aws ec2 create-key-pair \
  --key-name hello-world-key \
  --region eu-west-1 \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/hello-world-key.pem

# Set correct permissions
chmod 600 ~/.ssh/hello-world-key.pem
```

Then deploy with the key:

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1 \
  --parameter-overrides KeyName=hello-world-key
```

Connect to the instance:

```bash
# Get public IP
IP=$(aws cloudformation describe-stacks \
  --stack-name hello-world \
  --region eu-west-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
  --output text)

# SSH into the instance
ssh -i ~/.ssh/hello-world-key.pem ubuntu@$IP
```

### Manual Deployment

```bash
# Deploy stack (without SSH)
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1

# Deploy stack (with SSH access)
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1 \
  --parameter-overrides KeyName=hello-world-key

# Get outputs (IP, URL)
aws cloudformation describe-stacks \
  --stack-name hello-world \
  --region eu-west-1 \
  --query 'Stacks[0].Outputs' \
  --output table

# Delete stack
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

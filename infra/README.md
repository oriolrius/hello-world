# Infrastructure - v5.0.x

This folder contains the AWS infrastructure definition for the hello-world application.

## Quick Start

### Prerequisites

- AWS CLI configured with appropriate credentials
- EC2 Key Pair created in the target region (eu-west-1)

### Deploy

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --parameter-overrides KeyName=your-key-name AllowedIP=your-ip/32 \
  --region eu-west-1
```

### Verify

```bash
# Get the service URL
aws cloudformation describe-stacks \
  --stack-name hello-world \
  --query 'Stacks[0].Outputs[?OutputKey==`ServiceURL`].OutputValue' \
  --output text

# Test the service
curl http://<public-ip>:49000/
```

### Cleanup

```bash
aws cloudformation delete-stack --stack-name hello-world
```

## Stack Overview

| Component | Description |
|-----------|-------------|
| VPC | 10.0.0.0/16 with public subnet |
| EC2 | t3.micro Ubuntu 24.04 LTS |
| Security | Ports 22 (SSH) and 49000 (HTTP) |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| KeyName | (empty) | EC2 Key Pair name for SSH access |
| AllowedIP | 0.0.0.0/0 | CIDR allowed for SSH access |

## Files

| File | Description |
|------|-------------|
| `cloudformation.yml` | AWS CloudFormation template |
| `docs/ARCHITECTURE.md` | Detailed architecture documentation |
| `docs/infra-architecture.png` | Architecture diagram |
| `docs/infra-architecture.dot` | Graphviz source for diagram |
| `docs/infra-architecture.drawio` | Editable diagram (draw.io format) |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

![Infrastructure Architecture](docs/infra-architecture.png)

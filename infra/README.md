# Infrastructure

AWS CloudFormation template for deploying hello-world infrastructure.

## Quick Start

```bash
# Deploy
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1

# Get service URL
aws cloudformation describe-stacks \
  --stack-name hello-world \
  --query 'Stacks[0].Outputs[?OutputKey==`ServiceURL`].OutputValue' \
  --output text

# Destroy
aws cloudformation delete-stack --stack-name hello-world
```

## Stack Overview

Creates a minimal AWS environment:

- VPC with public subnet
- Internet Gateway with routing
- Security Group (ports 22, 49000)
- EC2 instance (t3.micro, Ubuntu 24.04)

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `KeyName` | EC2 Key Pair for SSH | (none) |
| `AllowedIP` | CIDR for SSH access | 0.0.0.0/0 |

## Files

| File | Description |
|------|-------------|
| `cloudformation.yml` | CloudFormation template |
| `docs/` | Architecture documentation |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

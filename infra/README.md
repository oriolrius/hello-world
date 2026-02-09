# Infrastructure

AWS infrastructure for the hello-world application, deployed via CloudFormation.

> **Architecture Diagram**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a visual diagram and detailed component descriptions.

## Quick Start

### Deploy

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1
```

### Get Service URL

```bash
aws cloudformation describe-stacks \
  --stack-name hello-world \
  --query 'Stacks[0].Outputs[?OutputKey==`ServiceURL`].OutputValue' \
  --output text
```

### Test

```bash
curl http://<public-ip>:49000
# Output: hello-world from <hostname>
```

### Delete

```bash
aws cloudformation delete-stack --stack-name hello-world --region eu-west-1
```

## Stack Overview

| Component | Value |
|-----------|-------|
| VPC CIDR | 10.0.0.0/16 |
| Subnet CIDR | 10.0.1.0/24 |
| Instance Type | t3.micro |
| OS | Ubuntu 24.04 LTS |
| App Port | 49000 |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `KeyName` | (none) | EC2 Key Pair for SSH |
| `AllowedIP` | 0.0.0.0/0 | Allowed SSH source IP |

## Files

| File | Purpose |
|------|---------|
| `cloudformation.yml` | Infrastructure as Code template |
| `docs/ARCHITECTURE.md` | Detailed architecture documentation |
| `docs/infra-architecture.png` | Infrastructure diagram |
| `docs/infra-architecture.drawio` | Editable diagram source |

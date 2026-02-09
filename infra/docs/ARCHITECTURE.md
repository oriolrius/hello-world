# CloudFormation Infrastructure Architecture (v3.0.x)

This document describes the AWS infrastructure for the hello-world application, deployed via CloudFormation.

## Architecture Diagram

![Infrastructure Architecture](infra-architecture.png)

> Editable version: [infra-architecture.drawio](infra-architecture.drawio) (open with [draw.io](https://app.diagrams.net/))

### Connection Color Legend

| Color | Line Style | Meaning |
|-------|------------|---------|
| **Green** | Bold | User HTTP traffic (port 49000) |
| **Blue** | Dashed | Admin SSH access (port 22) |
| **Gray** | Dotted | CloudFormation provisioning |

## Overview

The infrastructure is defined in `cloudformation.yml` and creates a simple single-EC2 deployment with networking components.

## Stack Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `KeyName` | (empty) | EC2 Key Pair name for SSH access |
| `AllowedIP` | `0.0.0.0/0` | IP CIDR allowed for SSH access |

## Resources Created

### Networking

| Resource | Type | Description |
|----------|------|-------------|
| `VPC` | AWS::EC2::VPC | VPC with CIDR 10.0.0.0/16 |
| `InternetGateway` | AWS::EC2::InternetGateway | Enables internet access |
| `AttachGateway` | AWS::EC2::VPCGatewayAttachment | Attaches IGW to VPC |
| `PublicSubnet` | AWS::EC2::Subnet | Public subnet 10.0.1.0/24 |
| `RouteTable` | AWS::EC2::RouteTable | Routes traffic |
| `Route` | AWS::EC2::Route | 0.0.0.0/0 → Internet Gateway |
| `SubnetRouteTableAssociation` | AWS::EC2::SubnetRouteTableAssociation | Associates subnet with route table |

### Security

| Resource | Type | Description |
|----------|------|-------------|
| `SecurityGroup` | AWS::EC2::SecurityGroup | Controls inbound traffic |

**Security Group Rules:**

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| Inbound | TCP | 49000 | 0.0.0.0/0 | Application traffic |
| Inbound | TCP | 22 | AllowedIP parameter | SSH access |

### Compute

| Resource | Type | Description |
|----------|------|-------------|
| `EC2Instance` | AWS::EC2::Instance | Application server |

**EC2 Instance Configuration:**

| Property | Value |
|----------|-------|
| Instance Type | t3.micro |
| AMI | Ubuntu 24.04 LTS (ami-0e9085e60087ce171) |
| Subnet | Public subnet (auto-assign public IP) |
| Key Pair | Optional (from KeyName parameter) |

## UserData Bootstrap

The EC2 instance runs a bootstrap script on first launch:

```bash
#!/bin/bash
# 1. Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install hello-world from GitHub
uv tool install hello-world --from git+https://github.com/oriolrius/hello-world

# 3. Create and enable systemd service
# - Binds to 0.0.0.0:49000
# - Auto-restart on failure
systemctl enable hello-world
systemctl start hello-world
```

## Stack Outputs

| Output | Description |
|--------|-------------|
| `PublicIP` | Public IP address of EC2 instance |
| `PublicDNS` | Public DNS name of EC2 instance |
| `ServiceURL` | Full URL to access the service (http://IP:49000) |

## Traffic Flow

### User Request (HTTP)

```
User → Internet → Internet Gateway → Public Subnet → EC2:49000
```

### Admin Access (SSH)

```
Admin → Internet → Internet Gateway → Public Subnet → EC2:22
```

## Deployment

### Deploy Stack

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1
```

### Deploy with SSH Access

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --parameter-overrides KeyName=my-keypair AllowedIP=1.2.3.4/32 \
  --region eu-west-1
```

### Get Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name hello-world \
  --query 'Stacks[0].Outputs' \
  --output table
```

### Delete Stack

```bash
aws cloudformation delete-stack --stack-name hello-world
```

> **Warning:** This deletes all resources and is irreversible.

## Cost Estimation

| Component | Monthly Cost |
|-----------|--------------|
| t3.micro EC2 | ~$8 (on-demand) |
| Data transfer | Variable |
| **Total** | **~$8-15/month** |

> **Tip:** Use t3.micro in free tier for the first 12 months.

## Security Considerations

| Item | Status | Recommendation |
|------|--------|----------------|
| SSH access | Open by default | Restrict AllowedIP parameter |
| HTTPS | Not configured | Add ALB with SSL certificate |
| Updates | Manual | Consider SSM for patching |
| Monitoring | None | Add CloudWatch alarms |

## Diagram Source

The architecture diagram was created using [draw.io](https://app.diagrams.net/).

**Base generation (optional):**

```bash
uv run tools/generate_infra_diagram.py
```

This produces a `.dot` file that can be converted to `.drawio` format using `graphviz2drawio`, then manually refined in draw.io.

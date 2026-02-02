# AWS Infrastructure Architecture - v5.0.x

This document describes the AWS infrastructure architecture for the hello-world application version 4.0.x.

## Architecture Diagram

![Infrastructure Architecture](infra-architecture.png)

## Connection Color Legend

| Color  | Description                              |
|--------|------------------------------------------|
| Blue   | HTTP traffic (port 49000)                |
| Green  | Allowed traffic through security group   |
| Orange | SSH access (port 22)                     |

## Overview

The infrastructure is deployed via AWS CloudFormation and consists of:

- **VPC** with public subnet
- **Internet Gateway** for public internet access
- **Route Table** for network routing
- **Security Group** for network access control
- **EC2 Instance** running the hello-world application

## CloudFormation Resources

### Network Resources

| Resource | Type | Description |
|----------|------|-------------|
| VPC | `AWS::EC2::VPC` | Virtual Private Cloud (10.0.0.0/16) |
| InternetGateway | `AWS::EC2::InternetGateway` | Internet gateway for public access |
| AttachGateway | `AWS::EC2::VPCGatewayAttachment` | Attaches IGW to VPC |
| PublicSubnet | `AWS::EC2::Subnet` | Public subnet (10.0.1.0/24) |
| RouteTable | `AWS::EC2::RouteTable` | Route table for subnet |
| Route | `AWS::EC2::Route` | Default route to Internet Gateway |
| SubnetRouteTableAssociation | `AWS::EC2::SubnetRouteTableAssociation` | Associates route table with subnet |

### Compute Resources

| Resource | Type | Description |
|----------|------|-------------|
| SecurityGroup | `AWS::EC2::SecurityGroup` | Controls inbound/outbound traffic |
| EC2Instance | `AWS::EC2::Instance` | Ubuntu 24.04 LTS (t3.micro) |

## Security Group Rules

### Inbound Rules

| Protocol | Port  | Source    | Description           |
|----------|-------|-----------|----------------------|
| TCP      | 49000 | 0.0.0.0/0 | HTTP (hello-world)   |
| TCP      | 22    | AllowedIP | SSH access           |

### Outbound Rules

All outbound traffic is allowed (default).

## Stack Parameters

| Parameter | Type   | Default     | Description               |
|-----------|--------|-------------|---------------------------|
| KeyName   | String | (empty)     | EC2 Key Pair for SSH      |
| AllowedIP | String | 0.0.0.0/0   | CIDR for SSH access       |

## Stack Outputs

| Output     | Description                    |
|------------|--------------------------------|
| PublicIP   | Public IP of EC2 instance      |
| PublicDNS  | Public DNS of EC2 instance     |
| ServiceURL | Hello World service URL        |

## Application Deployment

The application is deployed using Ansible after CloudFormation completes:

1. **uv** is installed on the EC2 instance
2. **hello-world** is installed as a uv tool from GitHub
3. A **systemd service** is created and started

### Systemd Service

The hello-world application runs as a systemd service:

- **Service name**: `hello-world`
- **Bind address**: `0.0.0.0:49000`
- **Auto-start**: Enabled on boot

## Deployment Commands

### Deploy the Stack

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --parameter-overrides KeyName=your-key-name
```

### Check Stack Status

```bash
aws cloudformation describe-stacks --stack-name hello-world
```

### Get Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name hello-world \
  --query 'Stacks[0].Outputs'
```

### Delete the Stack

```bash
aws cloudformation delete-stack --stack-name hello-world
```

## Cost Estimation

| Resource    | Type     | Estimated Monthly Cost |
|-------------|----------|------------------------|
| EC2         | t3.micro | ~$8 (on-demand)        |
| VPC/Network | -        | Free (within limits)   |
| Data Transfer | -      | Variable               |

**Note**: Costs vary by region and usage. Use AWS Pricing Calculator for accurate estimates.

## Security Considerations

1. **SSH Access**: Restrict `AllowedIP` parameter to your IP address
2. **Key Management**: Store EC2 private key securely
3. **Updates**: Regularly update the Ubuntu AMI for security patches
4. **HTTPS**: Consider adding an ALB with HTTPS for production use

## Diagram Source

The architecture diagram is generated using the [diagrams](https://diagrams.mingrammer.com/) library.

To regenerate the diagram:

```bash
cd tools
source .venv/bin/activate
python generate_infra_diagram.py
```

The editable `.drawio` file is also available for manual adjustments.

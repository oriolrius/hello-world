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

## Required AWS Permissions

The IAM user or role deploying this stack needs the following permissions:

### CloudFormation

| Action | Purpose |
|--------|---------|
| `cloudformation:CreateStack` | Create the stack |
| `cloudformation:UpdateStack` | Update existing stack |
| `cloudformation:DeleteStack` | Delete the stack |
| `cloudformation:DescribeStacks` | Get stack status and outputs |
| `cloudformation:DescribeStackEvents` | View deployment progress |
| `cloudformation:CreateChangeSet` | Preview changes (used by `aws cloudformation deploy`) |
| `cloudformation:ExecuteChangeSet` | Apply changes |
| `cloudformation:DescribeChangeSet` | View changeset details |
| `cloudformation:DeleteChangeSet` | Clean up changesets |

### EC2 (Networking)

| Action | Purpose |
|--------|---------|
| `ec2:CreateVpc` / `ec2:DeleteVpc` | Manage VPC |
| `ec2:CreateSubnet` / `ec2:DeleteSubnet` | Manage subnet |
| `ec2:CreateInternetGateway` / `ec2:DeleteInternetGateway` | Manage internet gateway |
| `ec2:AttachInternetGateway` / `ec2:DetachInternetGateway` | Connect IGW to VPC |
| `ec2:CreateRouteTable` / `ec2:DeleteRouteTable` | Manage route table |
| `ec2:CreateRoute` / `ec2:DeleteRoute` | Manage routes |
| `ec2:AssociateRouteTable` / `ec2:DisassociateRouteTable` | Link subnet to route table |
| `ec2:ModifyVpcAttribute` | Enable DNS settings |

### EC2 (Security & Instances)

| Action | Purpose |
|--------|---------|
| `ec2:CreateSecurityGroup` / `ec2:DeleteSecurityGroup` | Manage security group |
| `ec2:AuthorizeSecurityGroupIngress` / `ec2:RevokeSecurityGroupIngress` | Manage inbound rules |
| `ec2:RunInstances` / `ec2:TerminateInstances` | Manage EC2 instance |
| `ec2:DescribeInstances` | Get instance details |
| `ec2:DescribeImages` | Find AMI |
| `ec2:DescribeAvailabilityZones` | List AZs |
| `ec2:DescribeVpcs` / `ec2:DescribeSubnets` / `ec2:DescribeSecurityGroups` | Describe resources |
| `ec2:CreateTags` | Tag resources |

### EC2 (SSH Access - Optional)

| Action | Purpose |
|--------|---------|
| `ec2:CreateKeyPair` / `ec2:DeleteKeyPair` | Manage SSH key pairs |
| `ec2:DescribeKeyPairs` | List key pairs |

### Minimum IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*"
      ],
      "Resource": "arn:aws:cloudformation:*:*:stack/hello-world/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc", "ec2:DeleteVpc", "ec2:DescribeVpcs", "ec2:ModifyVpcAttribute",
        "ec2:CreateSubnet", "ec2:DeleteSubnet", "ec2:DescribeSubnets",
        "ec2:CreateInternetGateway", "ec2:DeleteInternetGateway", "ec2:DescribeInternetGateways",
        "ec2:AttachInternetGateway", "ec2:DetachInternetGateway",
        "ec2:CreateRouteTable", "ec2:DeleteRouteTable", "ec2:DescribeRouteTables",
        "ec2:CreateRoute", "ec2:DeleteRoute",
        "ec2:AssociateRouteTable", "ec2:DisassociateRouteTable",
        "ec2:CreateSecurityGroup", "ec2:DeleteSecurityGroup", "ec2:DescribeSecurityGroups",
        "ec2:AuthorizeSecurityGroupIngress", "ec2:RevokeSecurityGroupIngress",
        "ec2:RunInstances", "ec2:TerminateInstances", "ec2:DescribeInstances",
        "ec2:DescribeImages", "ec2:DescribeAvailabilityZones",
        "ec2:CreateKeyPair", "ec2:DeleteKeyPair", "ec2:DescribeKeyPairs",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

> **Note**: In AWS Sandbox environments, user roles may have limited permissions. Contact your administrator if deployments fail with "Access Denied" errors.

## Files

| File | Description |
|------|-------------|
| `cloudformation.yml` | CloudFormation template |
| `docs/` | Architecture documentation |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

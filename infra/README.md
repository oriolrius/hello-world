# Infrastructure

AWS CloudFormation template for deploying hello-world on ECS Fargate.

## Quick Start

```bash
# Deploy (requires ImageTag parameter)
make deploy

# Or manually:
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world-ecr-ecs-fargate \
  --parameter-overrides ImageTag=v4.3.3-ecr-ecs-fargate \
  --capabilities CAPABILITY_NAMED_IAM \
  --region eu-west-1

# Get service public IP
make status

# Or manually:
CLUSTER=hello-world-ecr-ecs-fargate
SERVICE=hello-world-ecr-ecs-fargate
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE --query 'taskArns[0]' --output text)
aws ecs describe-tasks --cluster $CLUSTER --tasks $TASK_ARN \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text | \
  xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} \
  --query 'NetworkInterfaces[0].Association.PublicIp' --output text

# Destroy
make delete

# Or manually:
aws cloudformation delete-stack --stack-name hello-world-ecr-ecs-fargate
```

## Stack Overview

Creates a serverless container environment on AWS:

| Resource | Description |
|----------|-------------|
| **ECR Repository** | Container image registry with lifecycle policy (keeps last 10 images) |
| **VPC** | Virtual network (10.0.0.0/16) with DNS enabled |
| **Public Subnet** | 10.0.1.0/24 with auto-assign public IP |
| **Internet Gateway** | Enables internet access |
| **Security Group** | Allows inbound TCP port 49000 |
| **ECS Cluster** | Fargate cluster for running containers |
| **ECS Task Definition** | 0.25 vCPU, 512MB memory, awsvpc network mode |
| **ECS Service** | Runs 1 task with public IP assignment |
| **CloudWatch Log Group** | Application logs with 7-day retention |
| **IAM Role** | Task execution role for ECR pull and logging |

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ImageTag` | Docker image tag to deploy (required) | - |
| `AllowedIP` | CIDR for application access | 0.0.0.0/0 |

Example image tags:
- `v4.3.3-ecr-ecs-fargate` (version tag)
- `sha-abc1234-ecr-ecs-fargate` (commit SHA tag)

## Outputs

| Output | Description |
|--------|-------------|
| `ECRRepositoryUri` | ECR repository URI for pushing images |
| `ECSClusterName` | ECS cluster name |
| `ECSServiceName` | ECS service name |
| `VPCId` | VPC ID |
| `SubnetId` | Public subnet ID |
| `SecurityGroupId` | Security group ID |

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
| `cloudformation:CreateChangeSet` | Preview changes |
| `cloudformation:ExecuteChangeSet` | Apply changes |
| `cloudformation:DescribeChangeSet` | View changeset details |
| `cloudformation:DeleteChangeSet` | Clean up changesets |

### ECR (Container Registry)

| Action | Purpose |
|--------|---------|
| `ecr:CreateRepository` / `ecr:DeleteRepository` | Manage ECR repository |
| `ecr:DescribeRepositories` | List repositories |
| `ecr:PutLifecyclePolicy` | Set image retention policy |
| `ecr:PutImageScanningConfiguration` | Enable vulnerability scanning |
| `ecr:GetAuthorizationToken` | Authenticate to ECR |
| `ecr:BatchCheckLayerAvailability` | Check image layers |
| `ecr:GetDownloadUrlForLayer` | Pull image layers |
| `ecr:BatchGetImage` | Pull images |
| `ecr:PutImage` | Push images |
| `ecr:InitiateLayerUpload` / `ecr:UploadLayerPart` / `ecr:CompleteLayerUpload` | Push image layers |

### ECS (Container Orchestration)

| Action | Purpose |
|--------|---------|
| `ecs:CreateCluster` / `ecs:DeleteCluster` | Manage ECS cluster |
| `ecs:DescribeClusters` | Get cluster details |
| `ecs:RegisterTaskDefinition` / `ecs:DeregisterTaskDefinition` | Manage task definitions |
| `ecs:DescribeTaskDefinition` | Get task definition details |
| `ecs:CreateService` / `ecs:DeleteService` / `ecs:UpdateService` | Manage ECS service |
| `ecs:DescribeServices` | Get service details |
| `ecs:ListTasks` / `ecs:DescribeTasks` | List and describe running tasks |

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
| `ec2:CreateSecurityGroup` / `ec2:DeleteSecurityGroup` | Manage security group |
| `ec2:AuthorizeSecurityGroupIngress` / `ec2:RevokeSecurityGroupIngress` | Manage inbound rules |
| `ec2:DescribeVpcs` / `ec2:DescribeSubnets` / `ec2:DescribeSecurityGroups` | Describe resources |
| `ec2:DescribeNetworkInterfaces` | Get task public IP |
| `ec2:ModifyVpcAttribute` | Enable DNS settings |
| `ec2:CreateTags` | Tag resources |

### IAM (Roles)

| Action | Purpose |
|--------|---------|
| `iam:CreateRole` / `iam:DeleteRole` | Manage ECS task execution role |
| `iam:AttachRolePolicy` / `iam:DetachRolePolicy` | Attach managed policies |
| `iam:PutRolePolicy` / `iam:DeleteRolePolicy` | Manage inline policies |
| `iam:GetRole` | Get role details |
| `iam:PassRole` | Allow ECS to use the role |

### CloudWatch Logs

| Action | Purpose |
|--------|---------|
| `logs:CreateLogGroup` / `logs:DeleteLogGroup` | Manage log group |
| `logs:PutRetentionPolicy` | Set log retention |
| `logs:DescribeLogGroups` / `logs:DescribeLogStreams` | List logs |
| `logs:GetLogEvents` | Read logs |

### Minimum IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "cloudformation:*",
      "Resource": "arn:aws:cloudformation:*:*:stack/hello-world-ecr-ecs-fargate/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:CreateRepository", "ecr:DeleteRepository", "ecr:DescribeRepositories",
        "ecr:PutLifecyclePolicy", "ecr:PutImageScanningConfiguration",
        "ecr:GetAuthorizationToken", "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage", "ecr:PutImage",
        "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload",
        "ecr:TagResource"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:CreateCluster", "ecs:DeleteCluster", "ecs:DescribeClusters",
        "ecs:RegisterTaskDefinition", "ecs:DeregisterTaskDefinition", "ecs:DescribeTaskDefinition",
        "ecs:CreateService", "ecs:DeleteService", "ecs:UpdateService", "ecs:DescribeServices",
        "ecs:ListTasks", "ecs:DescribeTasks", "ecs:TagResource"
      ],
      "Resource": "*"
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
        "ec2:DescribeNetworkInterfaces", "ec2:DescribeAvailabilityZones",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole", "iam:DeleteRole", "iam:GetRole",
        "iam:AttachRolePolicy", "iam:DetachRolePolicy",
        "iam:PutRolePolicy", "iam:DeleteRolePolicy",
        "iam:PassRole", "iam:TagRole"
      ],
      "Resource": "arn:aws:iam::*:role/hello-world-ecr-ecs-fargate-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup", "logs:DeleteLogGroup",
        "logs:PutRetentionPolicy", "logs:DescribeLogGroups",
        "logs:DescribeLogStreams", "logs:GetLogEvents", "logs:TagLogGroup"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/ecs/hello-world-ecr-ecs-fargate*"
    }
  ]
}
```

> **Note**: In AWS Sandbox environments, user roles may have limited permissions. Contact your administrator if deployments fail with "Access Denied" errors.

## Files

| File | Description |
|------|-------------|
| `cloudformation.yml` | CloudFormation template |
| `docs/ARCHITECTURE.md` | Detailed architecture documentation |
| `docs/infra-architecture.drawio` | Architecture diagram (editable) |
| `docs/infra-architecture.png` | Architecture diagram (rendered) |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation including:
- Resource diagrams
- Deployment procedures
- Cost estimation
- Security considerations
- Troubleshooting guide

# AWS Infrastructure Architecture (v4.x-ecr-ecs-fargate)

## Architecture Diagram

![AWS Infrastructure](infra-architecture.png)

Editable source: [infra-architecture.drawio](infra-architecture.drawio) (open with [draw.io](https://app.diagrams.net/))

## Overview

The v4.x-ecr-ecs-fargate infrastructure runs the hello-world application on AWS ECS Fargate with images stored in Amazon ECR. This serverless container deployment eliminates EC2 instance management while providing automatic scaling and high availability capabilities.

## Resources Created

### Container Registry

| Resource | Type | Configuration |
|----------|------|---------------|
| ECR Repository | AWS::ECR::Repository | hello-world, scan on push, lifecycle policy (keep 10 images) |

### Networking

| Resource | Type | Configuration |
|----------|------|---------------|
| VPC | AWS::EC2::VPC | CIDR: 10.0.0.0/16 |
| Internet Gateway | AWS::EC2::InternetGateway | Attached to VPC |
| Public Subnet | AWS::EC2::Subnet | CIDR: 10.0.1.0/24, Auto-assign public IP |
| Route Table | AWS::EC2::RouteTable | 0.0.0.0/0 -> Internet Gateway |
| Security Group | AWS::EC2::SecurityGroup | Inbound: 49000 (app) |

### Compute (ECS Fargate)

| Resource | Type | Configuration |
|----------|------|---------------|
| ECS Cluster | AWS::ECS::Cluster | hello-world |
| Task Definition | AWS::ECS::TaskDefinition | 0.25 vCPU, 512 MB, Fargate |
| ECS Service | AWS::ECS::Service | 1 desired task, public IP enabled |
| Execution Role | AWS::IAM::Role | ECR pull, CloudWatch logs |

### Logging

| Resource | Type | Configuration |
|----------|------|---------------|
| Log Group | AWS::Logs::LogGroup | /ecs/hello-world-ecr-ecs-fargate, 7 days retention |

## CloudFormation Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ImageTag` | Docker image tag to deploy | latest |
| `AllowedIP` | CIDR for application access | 0.0.0.0/0 |

## Stack Outputs

| Output | Description |
|--------|-------------|
| `ECRRepositoryUri` | ECR repository URI for pushing images |
| `ECSClusterName` | ECS cluster name |
| `ECSServiceName` | ECS service name |
| `VPCId` | VPC ID |
| `SubnetId` | Public subnet ID |
| `SecurityGroupId` | Security group ID |

## Deployment

### Prerequisites

- AWS CLI configured with appropriate credentials
- Docker installed and running

### Version Tagging

This branch uses the suffix `-ecr-ecs-fargate` for all version tags:
- Git tag: `v4.4.0-ecr-ecs-fargate`
- Docker image tag: `v4.4.0-ecr-ecs-fargate`

### Initial Deployment

1. Deploy the CloudFormation stack:

```bash
make deploy
```

2. Build and push the Docker image:

```bash
make ecr-push TAG=v4.4.0-ecr-ecs-fargate
```

3. Check service status:

```bash
make status
```

### Update Deployment

To deploy a new image version:

```bash
make ecr-push TAG=v4.5.0-ecr-ecs-fargate
make redeploy
```

### Force Redeployment (Same Image)

```bash
make redeploy
```

### View Logs

```bash
make logs
```

### Delete Stack

```bash
make delete
```

## Manual CLI Commands

### Deploy Stack

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world-ecr-ecs-fargate \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides ImageTag=v4.4.0-ecr-ecs-fargate \
  --region eu-west-1
```

### Get Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name hello-world-ecr-ecs-fargate \
  --query 'Stacks[0].Outputs' \
  --output table
```

### Get Task Public IP

```bash
TASK_ARN=$(aws ecs list-tasks --cluster hello-world-ecr-ecs-fargate --service-name hello-world-ecr-ecs-fargate --query 'taskArns[0]' --output text)
ENI_ID=$(aws ecs describe-tasks --cluster hello-world-ecr-ecs-fargate --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)
aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query 'NetworkInterfaces[0].Association.PublicIp' --output text
```

### Delete Stack

```bash
aws cloudformation delete-stack --stack-name hello-world-ecr-ecs-fargate
aws cloudformation wait stack-delete-complete --stack-name hello-world-ecr-ecs-fargate
```

## Cost Estimation

| Resource | Estimated Monthly Cost |
|----------|----------------------|
| Fargate (0.25 vCPU, 512MB, 24/7) | ~$10.00 |
| ECR storage | ~$0.10/GB |
| CloudWatch Logs | ~$0.50 |
| **Total** | ~$11/month |

## Security Considerations

| Aspect | Implementation |
|--------|----------------|
| Application Port | Configurable via `AllowedIP` parameter |
| Container Images | Scanned on push to ECR |
| IAM | Minimal permissions (ECR pull, CloudWatch logs) |
| Network | Public subnet with security group filtering |
| Secrets | Use AWS Secrets Manager for sensitive data (not implemented) |

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/release.yml`):

1. **lint** - Code quality checks with ruff
2. **test** - Run pytest
3. **build** - Build Python package
4. **release** - Create GitHub release
5. **docker** - Build and push to ECR

Deployment is manual via `make deploy` or `make redeploy`.

## Troubleshooting

### Task Not Starting

Check CloudWatch logs:
```bash
make logs
```

Or via AWS Console: CloudWatch > Log Groups > /ecs/hello-world-ecr-ecs-fargate

### No Public IP

Ensure the task is in RUNNING state:
```bash
make status
```

### Image Pull Errors

Verify the image exists in ECR:
```bash
aws ecr describe-images --repository-name hello-world-ecr-ecs-fargate --region eu-west-1
```

### Service Not Stabilizing

Check service events:
```bash
aws ecs describe-services --cluster hello-world-ecr-ecs-fargate --services hello-world-ecr-ecs-fargate \
  --query 'services[0].events[:5]' --output table
```

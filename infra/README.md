# EKS Cluster: esade-teaching

Target Kubernetes cluster for deploying the hello-world application.

## Cluster Overview

| Property | Value |
|----------|-------|
| **Cluster Name** | esade-teaching |
| **Region** | eu-west-1 (Ireland) |
| **Kubernetes Version** | 1.32 |
| **Platform** | Amazon EKS |
| **Created With** | eksctl v0.221.0 |

### API Endpoint
```
https://60B03161298E62303D99C8D3A6A5E5FB.gr7.eu-west-1.eks.amazonaws.com
```

## Node Configuration

| Property | Value |
|----------|-------|
| **Node Group** | students |
| **Instance Type** | t3.medium (2 vCPU, 4 GB RAM) |
| **AMI** | Amazon Linux 2023 |
| **Capacity** | ON_DEMAND |
| **Nodes** | 2 (min: 1, max: 3) |
| **Runtime** | containerd 2.1.5 |

## Networking

| Property | Value |
|----------|-------|
| **VPC CIDR** | 192.168.0.0/16 |
| **Service CIDR** | 10.100.0.0/16 |
| **Pod Networking** | AWS VPC CNI |

### Subnets

| Availability Zone | Public Subnet | Private Subnet |
|-------------------|---------------|----------------|
| eu-west-1a | 192.168.64.0/19 | 192.168.160.0/19 |
| eu-west-1b | 192.168.0.0/19 | 192.168.96.0/19 |
| eu-west-1c | 192.168.32.0/19 | 192.168.128.0/19 |

## EKS Add-ons

| Add-on | Version | Purpose |
|--------|---------|---------|
| vpc-cni | v1.20.4-eksbuild.2 | Pod networking |
| kube-proxy | v1.32.6-eksbuild.12 | Service proxy |
| coredns | v1.11.4-eksbuild.2 | Cluster DNS |
| metrics-server | v0.8.0-eksbuild.6 | Resource metrics |

## Storage

| Storage Class | Provisioner | Default |
|--------------|-------------|---------|
| gp2 | kubernetes.io/aws-ebs | Yes |

## Access Configuration

### Configure kubectl

```bash
aws eks update-kubeconfig --name esade-teaching --region eu-west-1
```

### Verify Access

```bash
kubectl cluster-info
kubectl get nodes -o wide
```

## CloudFormation Stacks

When you run `eksctl create cluster -f infra/eksctl-cluster.yaml`, eksctl translates the YAML configuration into AWS CloudFormation templates and creates these stacks:

| Stack | Created From | Purpose |
|-------|--------------|---------|
| eksctl-esade-teaching-cluster | `metadata` section | Control plane, VPC, subnets, IAM roles, security groups, internet gateway, NAT gateway |
| eksctl-esade-teaching-nodegroup-students | `managedNodeGroups[0]` section | EC2 instances, auto-scaling group, node IAM role, launch template |

This separation allows independent management:
- Scale or modify node groups without affecting the control plane
- Add additional node groups as separate stacks
- Delete node groups while keeping the cluster running

### View Stacks

```bash
aws cloudformation list-stacks --query "StackSummaries[?contains(StackName, 'esade-teaching')].[StackName,StackStatus]" --output table
```

### Stack Resources

```bash
# View cluster stack resources
aws cloudformation list-stack-resources --stack-name eksctl-esade-teaching-cluster --output table

# View nodegroup stack resources
aws cloudformation list-stack-resources --stack-name eksctl-esade-teaching-nodegroup-students --output table
```

## Cost Estimation

| Component | Monthly Cost |
|-----------|--------------|
| EKS Control Plane | ~$73 |
| 2x t3.medium nodes | ~$60 |
| NAT Gateway | ~$33 |
| **Total** | **~$166/month** |

## Cluster Management

### Scale Node Group

```bash
# Scale to 3 nodes
eksctl scale nodegroup --cluster=esade-teaching --name=students --nodes=3 --region=eu-west-1

# Scale down to 1 node
eksctl scale nodegroup --cluster=esade-teaching --name=students --nodes=1 --region=eu-west-1
```

### Delete Cluster

```bash
eksctl delete cluster --name esade-teaching --region eu-west-1
```

> **Warning:** This deletes all workloads and is irreversible.

## Security Notes

- API endpoint is publicly accessible (0.0.0.0/0)
- OIDC provider is disabled
- CloudWatch logging is disabled
- For production, consider enabling private endpoint and logging

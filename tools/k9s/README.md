# k9s - Kubernetes CLI Dashboard

[k9s](https://github.com/derailed/k9s) is a terminal-based UI to interact with your Kubernetes clusters.

## Installation

Download the k9s binary for your platform:

```bash
# Linux (amd64)
curl -sL "https://github.com/derailed/k9s/releases/download/v0.50.18/k9s_Linux_amd64.tar.gz" | tar -xz k9s

# macOS (Intel)
curl -sL "https://github.com/derailed/k9s/releases/download/v0.50.18/k9s_Darwin_amd64.tar.gz" | tar -xz k9s

# macOS (Apple Silicon)
curl -sL "https://github.com/derailed/k9s/releases/download/v0.50.18/k9s_Darwin_arm64.tar.gz" | tar -xz k9s
```

## Prerequisites: Configure kubectl for EKS

Before using k9s, configure kubectl to connect to your EKS cluster.

### 1. List available EKS clusters

```bash
aws eks list-clusters --region eu-west-1
```

### 2. Get cluster details

```bash
aws eks describe-cluster --name esade-teaching --region eu-west-1 \
  --query 'cluster.{name:name,status:status,version:version,endpoint:endpoint}'

# Or using eksctl
eksctl get cluster --region eu-west-1
```

### 3. Configure kubectl

```bash
aws eks update-kubeconfig --name esade-teaching --region eu-west-1
```

### 4. Verify configuration

```bash
kubectl config get-contexts
kubectl cluster-info
```

### 5. Discover namespaces

```bash
kubectl get namespaces
kubectl get all -n hello-world
```

## Usage

```bash
# Run k9s (uses current kubectl context)
./k9s

# Run k9s for a specific namespace
./k9s -n hello-world

# Run k9s for a specific context
./k9s --context <context-name>
```

Press `?` inside k9s for help.

## Links

- [k9s GitHub](https://github.com/derailed/k9s)
- [k9s Documentation](https://k9scli.io/)

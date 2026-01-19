# hello-world

A teaching project that demonstrates the evolution of DevOps practices. The application itself is intentionally trivial — a web server that returns "hello-world from \<hostname\>" — because the focus is on **how software is built, tested, and delivered**, not the application logic.

## What This Version Demonstrates (v6.x)

This version introduces **Container Orchestration** with Kubernetes on Amazon EKS, enabling horizontal scaling, self-healing, and declarative infrastructure:

| Practice | Implementation |
|----------|----------------|
| Container Orchestration | **Kubernetes (EKS)** |
| Infrastructure as Code | eksctl cluster definition |
| Declarative Deployment | Kubernetes manifests (YAML) |
| Service Discovery | Kubernetes Service + AWS ELB |
| Scaling | Horizontal Pod Autoscaling ready |
| Self-Healing | Liveness/readiness probes |

### Evolution from v5.x

- **v5.x**: Docker Compose on a single EC2 instance — one container, one host
- **v6.x**: **Kubernetes on EKS** — multiple pods across multiple nodes, load balanced

```
v5.x: EC2 → Docker Compose → 1 container
v6.x: EKS → Kubernetes → N pods across M nodes → LoadBalancer
```

### Why Kubernetes?

| Challenge | v5.x (Docker Compose) | v6.x (Kubernetes) |
|-----------|----------------------|-------------------|
| Scaling | Manual, single host | `kubectl scale --replicas=N` |
| High Availability | None (single point of failure) | Pods across nodes |
| Load Balancing | Manual (nginx) | Built-in (Service) |
| Self-Healing | Docker restart policy | Pod auto-restart + rescheduling |
| Rollback | Manual image tag change | `kubectl rollout undo` |
| Resource Limits | Manual | Declarative (requests/limits) |

**Key learning**: Kubernetes abstracts away individual servers, letting you think in terms of "desired state" rather than "these specific machines."

### The Hostname Feature

Notice the app now returns `hello-world from <hostname>`. This isn't just a code change — it demonstrates **load balancing verification**:

```bash
# Test load balancing across pods
for i in {1..10}; do curl -s http://$LB/; done
# hello-world from hello-world-abc123
# hello-world from hello-world-xyz789
# hello-world from hello-world-abc123
# ...
```

Different responses prove traffic is distributed across multiple pods.

---

## Quick Start

```bash
# Run locally
uv run hello-world

# Test
curl http://localhost:49000/
# Output: hello-world from <your-hostname>
```

## Development

```bash
uv sync                          # Install dependencies
uv run hello-world               # Run server
uv run ruff check src/ tests/    # Lint
uv run ruff format src/ tests/   # Format
uv run pytest -v                 # Test
```

### Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `-b, --bind` | Bind address | `0.0.0.0` |
| `-p, --port` | Port number | `49000` |

---

## EKS Deployment

Deploy to Amazon EKS with automated CI/CD via GitHub Actions.

### Architecture

![Architecture Overview](assets/diagrams/architecture.png)

### Prerequisites

- AWS CLI configured with valid credentials
- kubectl installed
- eksctl installed (for cluster creation)
- Access to GitHub repository secrets

---

## 1. Create EKS Cluster

Create the cluster using eksctl:

```bash
eksctl create cluster -f infra/eksctl-cluster.yaml
```

This creates two **AWS CloudFormation stacks**:

| Stack | Purpose |
|-------|---------|
| `eksctl-esade-teaching-cluster` | Control plane, VPC, subnets, networking |
| `eksctl-esade-teaching-nodegroup-students` | EC2 nodes, auto-scaling group |

Resources provisioned:
- EKS cluster `esade-teaching` in `eu-west-1`
- Managed node group with 2x t3.medium instances
- VPC with public/private subnets
- Required add-ons (vpc-cni, coredns, kube-proxy, metrics-server)

### Verify Cluster

```bash
# Configure kubectl
aws eks update-kubeconfig --name esade-teaching --region eu-west-1

# Verify access
kubectl cluster-info
kubectl get nodes
```

See [infra/README.md](infra/README.md) for detailed cluster documentation.

---

## 2. Configure GitHub Secrets

Set AWS credentials for GitHub Actions:

```bash
gh secret set AWS_ACCESS_KEY_ID --body "your-access-key"
gh secret set AWS_SECRET_ACCESS_KEY --body "your-secret-key"
gh secret set AWS_SESSION_TOKEN --body "your-session-token"  # if using SSO
```

---

## 3. CI/CD Pipeline

The release workflow (`.github/workflows/release.yml`) triggers on:
- Push to tags matching `v*`
- Manual dispatch (`workflow_dispatch`)

### Pipeline Steps

| Job | Description |
|-----|-------------|
| **lint** | Runs `ruff check` and `ruff format --check` |
| **test** | Runs `pytest` |
| **docker** | Builds and pushes image to `ghcr.io/oriolrius/hello-world` |
| **deploy** | Deploys to EKS and verifies load balancing |

### Verification

The deploy job verifies:
- All pods are running and healthy
- Response format is correct (`hello-world from <pod-name>`)
- Load balancer distributes traffic to multiple pods

### Trigger Deployment

```bash
# Create and push a tag
git tag v6.1.0
git push origin v6.1.0

# Or trigger manually
gh workflow run release.yml
```

---

## 4. Manual Kubernetes Operations

### Deploy

```bash
kubectl apply -k k8s/
kubectl rollout status deployment/hello-world -n hello-world
```

### Verify

```bash
# Check pods
kubectl get pods -n hello-world -o wide

# Get LoadBalancer URL
LB=$(kubectl get svc -n hello-world hello-world -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "URL: http://$LB/"

# Test load balancing
for i in {1..10}; do curl -s http://$LB/; done
```

### Scale

```bash
# Scale to 4 replicas
kubectl scale deployment/hello-world -n hello-world --replicas=4

# Scale down to 2
kubectl scale deployment/hello-world -n hello-world --replicas=2
```

### Update Image

```bash
kubectl set image deployment/hello-world -n hello-world \
  hello-world=ghcr.io/oriolrius/hello-world:v6.1.0

kubectl rollout status deployment/hello-world -n hello-world
```

### Rollback

```bash
kubectl rollout undo deployment/hello-world -n hello-world
```

See [k8s/README.md](k8s/README.md) for detailed Kubernetes operations and failure recovery simulation.

---

## 5. Cleanup

### Remove Application

```bash
kubectl delete -k k8s/
```

### Destroy EKS Cluster

```bash
eksctl delete cluster --name esade-teaching --region eu-west-1
```

> **Warning:** This deletes all workloads and is irreversible.

---

## Documentation

| Document | Description |
|----------|-------------|
| [k8s/README.md](k8s/README.md) | Kubernetes deployment guide, scaling, failure recovery simulation, troubleshooting |
| [k8s/docs/ARCHITECTURE.md](k8s/docs/ARCHITECTURE.md) | Kubernetes architecture diagram |
| [infra/README.md](infra/README.md) | EKS cluster documentation, networking, add-ons, management commands |
| [infra/docs/ARCHITECTURE.md](infra/docs/ARCHITECTURE.md) | EKS infrastructure architecture diagram |
| [.github/workflows/README.md](.github/workflows/README.md) | CI/CD pipeline documentation |
| [.github/workflows/docs/ARCHITECTURE.md](.github/workflows/docs/ARCHITECTURE.md) | CI/CD pipeline architecture diagram |

---

## Project Structure

```
hello-world/
├── src/hello_world/       # Application code
├── tests/                 # Tests
├── docker/
│   ├── Dockerfile         # Container image
│   └── .dockerignore
├── k8s/
│   ├── namespace.yaml     # Kubernetes namespace
│   ├── deployment.yaml    # Deployment (2 replicas, health probes)
│   ├── service.yaml       # LoadBalancer service
│   ├── kustomization.yaml # Kustomize config
│   ├── README.md          # K8s operations guide
│   └── docs/              # Architecture documentation
├── infra/
│   ├── eksctl-cluster.yaml # EKS cluster definition
│   ├── README.md           # Cluster documentation
│   └── docs/               # Architecture documentation
├── .github/workflows/
│   ├── release.yml        # CI/CD pipeline
│   ├── README.md          # Workflow documentation
│   └── docs/              # Architecture documentation
└── tools/                 # Diagram generation scripts
```

---

## Cost Estimation (EKS)

| Component | Monthly Cost |
|-----------|--------------|
| EKS Control Plane | ~$73 |
| 2x t3.medium nodes | ~$60 |
| NAT Gateway | ~$33 |
| Load Balancer | ~$18 |
| **Total** | **~$184/month** |

---

## License

MIT

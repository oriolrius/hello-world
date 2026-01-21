# Headlamp - Kubernetes Web Dashboard

[Headlamp](https://headlamp.dev/) is a web-based Kubernetes dashboard for monitoring and managing clusters.

## Architecture

```
User Browser
     |
     v
AWS LoadBalancer:80
     |
     v
Headlamp (Token Auth)
  - Token from admin-user ServiceAccount
     |
     v
Kubernetes API Server
```

## Prerequisites

### 1. Configure kubectl for EKS

```bash
# List available clusters
aws eks list-clusters --region eu-west-1

# Configure kubectl
aws eks update-kubeconfig --name esade-teaching --region eu-west-1

# Verify connection
kubectl cluster-info
```

### 2. Install Helm

```bash
# Check if helm is installed
helm version

# If not, install it
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## Quick Deploy

```bash
cd tools/headlamp
./deploy.sh
```

## Manual Deployment

### Step 1: Create namespace

```bash
kubectl apply -f namespace.yaml
```

**Source:** `namespace.yaml`
- Creates `headlamp` namespace to isolate all Headlamp resources

### Step 2: Add Helm repository

```bash
helm repo add headlamp https://kubernetes-sigs.github.io/headlamp/
helm repo update
```

**Source:** Official Headlamp Helm chart from https://github.com/headlamp-k8s/headlamp

### Step 3: Install Headlamp

```bash
helm upgrade --install headlamp headlamp/headlamp \
  --namespace headlamp \
  --values values.yaml \
  --wait
```

**Source:** `values.yaml`

| Parameter | Value | Why |
|-----------|-------|-----|
| `config.inCluster` | `true` | Headlamp runs inside cluster, uses ServiceAccount for API access |
| `service.type` | `LoadBalancer` | Exposes Headlamp directly via AWS ELB |
| `service.port` | `80` | Default HTTP port |
| `serviceAccount.create` | `true` | Required for Headlamp to access Kubernetes API |
| `clusterRoleBinding.clusterRoleName` | `cluster-admin` | Full cluster access for dashboard |

### Step 4: Create admin user

```bash
kubectl apply -f admin-user.yaml
```

**Source:** `admin-user.yaml`

| Resource | Purpose |
|----------|---------|
| `ServiceAccount/admin-user` | Identity for dashboard login |
| `ClusterRoleBinding/headlamp-admin-user` | Grants `cluster-admin` role |
| `Secret/admin-user-token` | Stores persistent auth token |

**Why ServiceAccount?**
- Headlamp authenticates via Kubernetes tokens, not username/password
- ServiceAccount provides a token that grants API access
- ClusterRoleBinding defines what the token can do

## Access the Dashboard

### Get the URL

```bash
kubectl get svc headlamp -n headlamp -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

The URL format is: `http://<loadbalancer-hostname>`

### Authentication

Get the token:
```bash
kubectl get secret admin-user-token -n headlamp -o jsonpath='{.data.token}' | base64 -d
```

Paste the token in Headlamp's login screen.

## Configuration Reference

### Service Type

Defined in `values.yaml`:
```yaml
service:
  type: LoadBalancer
  port: 80
```

The Headlamp service is exposed directly via AWS LoadBalancer on port 80.

## Uninstall

```bash
# Remove all resources
helm uninstall headlamp -n headlamp
kubectl delete -f admin-user.yaml
kubectl delete -f namespace.yaml
```

## Troubleshooting

### Check pod status
```bash
kubectl get pods -n headlamp
```

### Check Headlamp logs
```bash
kubectl logs -n headlamp -l app.kubernetes.io/name=headlamp
```

### LoadBalancer not getting external IP
```bash
# Check service status
kubectl describe svc headlamp -n headlamp

# AWS LoadBalancer can take 2-3 minutes to provision
```

### Token authentication not working
```bash
# Verify the admin-user ServiceAccount exists
kubectl get sa admin-user -n headlamp

# Verify the token secret exists
kubectl get secret admin-user-token -n headlamp

# Test token validity
kubectl auth can-i get pods --as=system:serviceaccount:headlamp:admin-user
```

## Optional: Basic Auth Proxy

If you need an additional layer of HTTP Basic Authentication in front of Headlamp, you can deploy the nginx proxy:

```bash
kubectl apply -f basic-auth-proxy.yaml
```

This creates:
- nginx proxy with Basic Auth (admin / The2password.)
- LoadBalancer on port 49100

Access via: `http://<proxy-loadbalancer>:49100`

## Links

- [Headlamp Documentation](https://headlamp.dev/docs/)
- [Headlamp GitHub](https://github.com/headlamp-k8s/headlamp)
- [Helm Chart Values](https://github.com/headlamp-k8s/headlamp/blob/main/charts/headlamp/values.yaml)

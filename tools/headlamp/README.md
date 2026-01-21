# Headlamp - Kubernetes Web Dashboard

[Headlamp](https://headlamp.dev/) is a web-based Kubernetes dashboard for monitoring and managing clusters.

## Architecture

```
User Browser
     |
     v
AWS LoadBalancer:49100
     |
     v
nginx (Basic Auth)  ─────────────────────┐
  - Username: admin                      │
  - Password: The2password.              │
     |                                   │
     v                                   │
Headlamp (Token Auth)                    │
  - Token from admin-user ServiceAccount │
     |                                   │
     v                                   │
Kubernetes API Server <──────────────────┘
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
| `service.type` | `ClusterIP` | Internal only, nginx proxy exposes externally |
| `service.port` | `80` | Default HTTP port, proxied by nginx |
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

### Step 5: Deploy basic auth proxy

```bash
kubectl apply -f basic-auth-proxy.yaml
```

**Source:** `basic-auth-proxy.yaml`

| Resource | Purpose |
|----------|---------|
| `ConfigMap/basic-auth-htpasswd` | Stores `admin:The2password.` credentials |
| `ConfigMap/nginx-config` | nginx configuration for proxy |
| `Deployment/headlamp-proxy` | nginx container with basic auth |
| `Service/headlamp-proxy` | LoadBalancer on port 49100 |

**Why nginx proxy?**
- Headlamp uses token auth, not username/password
- nginx adds HTTP Basic Auth layer
- Allows "admin / The2password." authentication requirement
- Proxies authenticated requests to Headlamp

**How htpasswd was generated:**
```bash
htpasswd -nb admin 'The2password.'
# Output: admin:$apr1$6r/qWWIV$bsDcC/XvWiHNWLKuN2IIl1
```

## Access the Dashboard

### Get the URL

```bash
kubectl get svc headlamp-proxy -n headlamp -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

The URL format is: `http://<loadbalancer-hostname>:49100`

### Authentication (2 steps)

**Step 1: Basic Auth (nginx)**
- Username: `admin`
- Password: `The2password.`

**Step 2: Token Auth (Headlamp)**

Get the token:
```bash
kubectl get secret admin-user-token -n headlamp -o jsonpath='{.data.token}' | base64 -d
```

Paste the token in Headlamp's login screen.

## Configuration Reference

### Port 49100

Defined in `basic-auth-proxy.yaml`:
```yaml
spec:
  ports:
    - port: 49100      # External LoadBalancer port
      targetPort: 49100 # nginx container port
```

And in nginx config:
```nginx
server {
    listen 49100;  # nginx listens on this port
    ...
}
```

### Credentials (admin / The2password.)

Defined in `basic-auth-proxy.yaml`:
```yaml
data:
  htpasswd: |
    admin:$apr1$6r/qWWIV$bsDcC/XvWiHNWLKuN2IIl1
```

To change credentials:
```bash
# Generate new htpasswd
htpasswd -nb <username> '<password>'

# Update ConfigMap and restart proxy
kubectl rollout restart deployment/headlamp-proxy -n headlamp
```

## Uninstall

```bash
# Remove all resources
helm uninstall headlamp -n headlamp
kubectl delete -f basic-auth-proxy.yaml
kubectl delete -f admin-user.yaml
kubectl delete -f namespace.yaml
```

## Troubleshooting

### Check pod status
```bash
kubectl get pods -n headlamp
```

### Check proxy logs
```bash
kubectl logs -n headlamp -l app.kubernetes.io/name=headlamp-proxy
```

### Check Headlamp logs
```bash
kubectl logs -n headlamp -l app.kubernetes.io/name=headlamp
```

### LoadBalancer not getting external IP
```bash
# Check service status
kubectl describe svc headlamp-proxy -n headlamp

# AWS LoadBalancer can take 2-3 minutes to provision
```

## Links

- [Headlamp Documentation](https://headlamp.dev/docs/)
- [Headlamp GitHub](https://github.com/headlamp-k8s/headlamp)
- [Helm Chart Values](https://github.com/headlamp-k8s/headlamp/blob/main/charts/headlamp/values.yaml)

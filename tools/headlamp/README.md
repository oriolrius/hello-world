# Headlamp - Kubernetes Web Dashboard

[Headlamp](https://headlamp.dev/) is a web-based Kubernetes dashboard running inside the `esade-teaching` EKS cluster, providing visibility and management of cluster resources.

## Desired State

| Property | Value |
|----------|-------|
| Namespace | `headlamp` |
| Replicas | 1 |
| Mode | In-cluster (ServiceAccount-based API access) |
| Exposure | AWS LoadBalancer on port 80 |
| Auth | Token from `admin-user` ServiceAccount (`cluster-admin`) |

### Resources

Tuned for `t3a.small` nodes (2 vCPU, 2 GB RAM), leaving headroom for system pods:

| | CPU | Memory |
|-|-----|--------|
| Request | 50m | 64Mi |
| Limit | 200m | 128Mi |

## Architecture

```
User Browser
     |
     v
AWS ELB :80  (provisioned by service.type: LoadBalancer)
     |
     v
Headlamp Pod  (namespace: headlamp)
     |
     v
Kubernetes API Server  (via headlamp ServiceAccount, cluster-admin)
```

## Manifests

| File | Purpose |
|------|---------|
| `namespace.yaml` | Isolates all Headlamp resources in the `headlamp` namespace |
| `values.yaml` | Helm values — in-cluster mode, LoadBalancer service, resource limits |
| `admin-user.yaml` | ServiceAccount + ClusterRoleBinding + persistent token Secret for login |
| `basic-auth-proxy.yaml` | Optional nginx proxy adding HTTP Basic Auth on port 49100 |

### Admin User (`admin-user.yaml`)

Creates three resources in the `headlamp` namespace:

- `ServiceAccount/admin-user` — identity used to log in to the dashboard
- `ClusterRoleBinding/headlamp-admin-user` — binds `admin-user` to `cluster-admin`
- `Secret/admin-user-token` — persistent token (type `kubernetes.io/service-account-token`)

Headlamp authenticates via Kubernetes bearer tokens. The admin-user token grants full cluster visibility.

## Deployment

```bash
cd tools/headlamp && ./deploy.sh
```

The script: creates the namespace, installs the Helm chart with `values.yaml`, applies `admin-user.yaml`, and waits for rollout.

### Get access token

```bash
kubectl get secret admin-user-token -n headlamp -o jsonpath='{.data.token}' | base64 -d
```

### Get LoadBalancer URL

```bash
kubectl get svc headlamp -n headlamp -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## Uninstall

```bash
helm uninstall headlamp -n headlamp
kubectl delete -f admin-user.yaml
kubectl delete -f namespace.yaml
```

## Links

- [Headlamp Documentation](https://headlamp.dev/docs/)
- [Helm Chart Values Reference](https://github.com/headlamp-k8s/headlamp/blob/main/charts/headlamp/values.yaml)

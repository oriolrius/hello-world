# Kubernetes Deployment Guide

Deploy hello-world to the **esade-teaching** EKS cluster.

## Prerequisites

1. AWS CLI configured with valid credentials
2. kubectl installed
3. Access to the esade-teaching EKS cluster

### Configure kubectl

```bash
aws eks update-kubeconfig --name esade-teaching --region eu-west-1
```

### Verify Cluster Access

```bash
kubectl cluster-info
kubectl get nodes
```

Expected output:
```
NAME                                           STATUS   ROLES    AGE   VERSION
ip-192-168-41-74.eu-west-1.compute.internal    Ready    <none>   1d    v1.32.x
ip-192-168-74-132.eu-west-1.compute.internal   Ready    <none>   1d    v1.32.x
```

---

## Deploy

### Using Kustomize (Recommended)

```bash
kubectl apply -k k8s/
```

### Using Individual Files

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Expected Output

```
namespace/hello-world created
service/hello-world created
deployment.apps/hello-world created
```

---

## Verify Deployment

### Check All Resources

```bash
kubectl get all -n hello-world
```

Expected output:
```
NAME                               READY   STATUS    RESTARTS   AGE
pod/hello-world-85df8f77cb-xxxxx   1/1     Running   0          1m
pod/hello-world-85df8f77cb-yyyyy   1/1     Running   0          1m

NAME                  TYPE           CLUSTER-IP      EXTERNAL-IP                                    PORT(S)        AGE
service/hello-world   LoadBalancer   10.100.x.x      xxxxx.eu-west-1.elb.amazonaws.com              80:30xxx/TCP   1m

NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-world   2/2     2            2           1m
```

### Check Pod Status

```bash
kubectl get pods -n hello-world -o wide
```

### Check Pod Logs

```bash
kubectl logs -n hello-world -l app.kubernetes.io/name=hello-world
```

### Describe Deployment

```bash
kubectl describe deployment -n hello-world hello-world
```

---

## Test the Application

### Get LoadBalancer URL

```bash
kubectl get svc -n hello-world hello-world -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### Test with curl

```bash
# Get the URL
LB_URL=$(kubectl get svc -n hello-world hello-world -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Test the service
curl http://$LB_URL/
```

Expected output:
```
hello-world
```

### Test Multiple Times (Load Balancing)

```bash
for i in {1..10}; do curl -s http://$LB_URL/; echo; done
```

---

## Scaling

### Scale Up

```bash
kubectl scale deployment -n hello-world hello-world --replicas=4
```

### Scale Down

```bash
kubectl scale deployment -n hello-world hello-world --replicas=2
```

### Watch Scaling

```bash
kubectl get pods -n hello-world -w
```

---

## Failure Recovery Simulation

Kubernetes automatically recovers from pod failures. Here's how to test it:

### 1. Check Current Pods

```bash
kubectl get pods -n hello-world -o wide
```

Note the pod names and nodes.

### 2. Delete a Pod (Simulate Failure)

```bash
# Get pod name
POD_NAME=$(kubectl get pods -n hello-world -o jsonpath='{.items[0].metadata.name}')

# Delete the pod
kubectl delete pod -n hello-world $POD_NAME
```

### 3. Watch Recovery

```bash
kubectl get pods -n hello-world -w
```

Expected behavior:
```
NAME                           READY   STATUS        RESTARTS   AGE
hello-world-85df8f77cb-xxxxx   1/1     Terminating   0          5m
hello-world-85df8f77cb-yyyyy   1/1     Running       0          5m
hello-world-85df8f77cb-zzzzz   0/1     Pending       0          0s
hello-world-85df8f77cb-zzzzz   0/1     ContainerCreating   0   0s
hello-world-85df8f77cb-zzzzz   1/1     Running       0          3s
```

The deployment controller automatically creates a new pod to maintain the desired replica count.

### 4. Verify Service Continuity

While the pod is recovering, the service continues to work:

```bash
# Run this in a loop during recovery
while true; do curl -s http://$LB_URL/ && echo " - $(date)"; sleep 1; done
```

### 5. Simulate Node Failure

To test recovery from node issues, cordon a node:

```bash
# Get node name
NODE=$(kubectl get pods -n hello-world -o jsonpath='{.items[0].spec.nodeName}')

# Cordon the node (prevent new pods)
kubectl cordon $NODE

# Delete pods on that node
kubectl delete pods -n hello-world --field-selector spec.nodeName=$NODE

# Watch pods reschedule to other nodes
kubectl get pods -n hello-world -o wide -w

# Uncordon when done
kubectl uncordon $NODE
```

---

## Health Checks

The deployment includes liveness and readiness probes:

### Liveness Probe
- **Path:** `/`
- **Port:** 49000
- **Initial Delay:** 5s
- **Period:** 10s
- **Failure Threshold:** 3

If the liveness probe fails 3 times, Kubernetes restarts the container.

### Readiness Probe
- **Path:** `/`
- **Port:** 49000
- **Initial Delay:** 5s
- **Period:** 5s
- **Failure Threshold:** 3

If the readiness probe fails, the pod is removed from the service endpoints.

### Check Probe Status

```bash
kubectl describe pod -n hello-world -l app.kubernetes.io/name=hello-world | grep -A5 "Liveness\|Readiness"
```

---

## Update Deployment

### Update Image Tag

```bash
kubectl set image deployment/hello-world -n hello-world hello-world=ghcr.io/oriolrius/hello-world:6.0.0
```

### Watch Rollout

```bash
kubectl rollout status deployment/hello-world -n hello-world
```

### Rollback

```bash
kubectl rollout undo deployment/hello-world -n hello-world
```

### View Rollout History

```bash
kubectl rollout history deployment/hello-world -n hello-world
```

---

## Remove Deployment

### Using Kustomize

```bash
kubectl delete -k k8s/
```

### Using Individual Files

```bash
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/namespace.yaml
```

### Verify Removal

```bash
kubectl get all -n hello-world
# Should return: No resources found in hello-world namespace.

kubectl get ns hello-world
# Should return: Error from server (NotFound): namespaces "hello-world" not found
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check events
kubectl get events -n hello-world --sort-by='.lastTimestamp'

# Describe pod
kubectl describe pod -n hello-world -l app.kubernetes.io/name=hello-world
```

### Service Not Accessible

```bash
# Check endpoints
kubectl get endpoints -n hello-world

# Check service
kubectl describe svc -n hello-world hello-world
```

### LoadBalancer Pending

If EXTERNAL-IP shows `<pending>`:

```bash
# Check AWS Load Balancer Controller or wait 2-5 minutes for ELB provisioning
kubectl describe svc -n hello-world hello-world
```

### Image Pull Errors

```bash
# Check if image is accessible
docker pull ghcr.io/oriolrius/hello-world:latest

# Check pod events
kubectl describe pod -n hello-world -l app.kubernetes.io/name=hello-world | grep -A10 Events
```

---

## Manifest Files

| File | Description |
|------|-------------|
| `namespace.yaml` | Creates `hello-world` namespace |
| `deployment.yaml` | Deploys 2 replicas with health probes |
| `service.yaml` | LoadBalancer service on port 80 |
| `kustomization.yaml` | Kustomize configuration |

---

## Resource Specifications

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 50m | 200m |
| Memory | 64Mi | 128Mi |

With 2 replicas:
- **Total CPU:** 100m request, 400m limit
- **Total Memory:** 128Mi request, 256Mi limit

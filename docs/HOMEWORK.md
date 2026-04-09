# Session 7 Assignment: Deploy hello-world to Kubernetes (EKS)

## Objective

Deploy the **hello-world** application to a shared Amazon EKS cluster, verify load balancing across multiple pods, demonstrate scaling and self-healing, and clean up after yourself.

---

## Instructor Setup (Reference Only)

> This section documents how the instructor prepares the shared cluster before class. Students do not need to perform these steps.

### 1. EKS Cluster

The cluster `esade-teaching` is already running in `eu-west-1` (Ireland), created with:

```bash
eksctl create cluster -f infra/eksctl-cluster.yaml
```

| Property | Value |
|----------|-------|
| Cluster name | `esade-teaching` |
| Region | `eu-west-1` |
| Kubernetes version | 1.32 |
| Node group | `students` (2x t3a.small, auto-scaling 1-3) |
| Cost | ~$166/month (~$41/week) |

### 2. Create Per-Student Namespaces

Each student gets an isolated namespace with RBAC restrictions:

```bash
#!/bin/bash
# run-once-per-student.sh
STUDENTS="alice bob carlos diana ..."

for STUDENT in $STUDENTS; do
  NS="hw-${STUDENT}"

  # Create namespace
  kubectl create namespace ${NS}

  # Role: full access within their namespace only
  kubectl -n ${NS} apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: student-admin
  namespace: ${NS}
rules:
  - apiGroups: ["", "apps", "autoscaling"]
    resources: ["*"]
    verbs: ["*"]
EOF

  # ServiceAccount
  kubectl -n ${NS} create serviceaccount ${STUDENT}

  # Bind role to service account
  kubectl -n ${NS} create rolebinding ${STUDENT}-admin \
    --role=student-admin \
    --serviceaccount=${NS}:${STUDENT}

  # Long-lived token
  kubectl -n ${NS} apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: ${STUDENT}-token
  annotations:
    kubernetes.io/service-account.name: ${STUDENT}
type: kubernetes.io/service-account-token
EOF

  # ResourceQuota (prevent one student from consuming the cluster)
  kubectl -n ${NS} apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: student-quota
spec:
  hard:
    pods: "10"
    requests.cpu: "500m"
    requests.memory: "512Mi"
    limits.cpu: "1"
    limits.memory: "1Gi"
    services.loadbalancers: "0"
EOF

  # LimitRange (default resource specs for pods without explicit limits)
  kubectl -n ${NS} apply -f - <<EOF
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
    - default:
        cpu: 200m
        memory: 128Mi
      defaultRequest:
        cpu: 50m
        memory: 64Mi
      type: Container
EOF
done
```

> **Note:** `services.loadbalancers: "0"` prevents students from creating AWS ELBs (which cost money and take time to provision). Students will use `kubectl port-forward` instead.

### 3. Generate Per-Student Kubeconfig Files

```bash
SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
CA=$(kubectl config view --raw --minify -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')

for STUDENT in $STUDENTS; do
  NS="hw-${STUDENT}"
  TOKEN=$(kubectl -n ${NS} get secret ${STUDENT}-token \
    -o jsonpath='{.data.token}' | base64 -d)

  cat > kubeconfig-${STUDENT}.yaml <<EOF
apiVersion: v1
kind: Config
clusters:
  - cluster:
      server: ${SERVER}
      certificate-authority-data: ${CA}
    name: esade-teaching
contexts:
  - context:
      cluster: esade-teaching
      namespace: ${NS}
      user: ${STUDENT}
    name: ${STUDENT}@esade-teaching
current-context: ${STUDENT}@esade-teaching
users:
  - name: ${STUDENT}
    user:
      token: ${TOKEN}
EOF
done
```

### 4. Distribute

Upload each `kubeconfig-<student>.yaml` to **eCampus** as a private per-student file (or send individually via email).

### 5. Cleanup After Deadline

```bash
for STUDENT in $STUDENTS; do
  kubectl delete namespace hw-${STUDENT}
done

# Optionally scale down to reduce costs
eksctl scale nodegroup --cluster=esade-teaching \
  --name=students --nodes=1 --region=eu-west-1
```

---

## Student Assignment

### Prerequisites

Before you start, make sure you have:

- **kubectl** installed ([install guide](https://kubernetes.io/docs/tasks/tools/))
- Your personal **kubeconfig file** downloaded from eCampus (`kubeconfig-<yourname>.yaml`)
- Basic familiarity with the terminal

### Deadline

**Before Session 8 (15 April 2026)**

---

### Step 1: Configure Cluster Access

Set the `KUBECONFIG` environment variable to point to your personal kubeconfig file:

```bash
export KUBECONFIG=~/Downloads/kubeconfig-<yourname>.yaml
```

Verify access:

```bash
kubectl get pods
```

Expected output:

```
No resources found in hw-<yourname> namespace.
```

This confirms you are connected to the cluster and scoped to your own namespace. You cannot see or modify other students' namespaces.

> **Tip:** Add the `export KUBECONFIG=...` line to your `~/.bashrc` or `~/.zshrc` to avoid repeating it in every terminal session.

---

### Step 2: Clone the Repository

```bash
git clone https://github.com/oriolrius/hello-world.git
cd hello-world
git checkout v6.x
```

---

### Step 3: Deploy the Application

Since your kubeconfig is already scoped to your namespace (`hw-<yourname>`), you need to deploy the individual manifests **without** the namespace resource (which you don't have permission to create):

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

> **Why not `kubectl apply -k k8s/`?** The Kustomize bundle includes `namespace.yaml` which tries to create the `hello-world` namespace. Your namespace (`hw-<yourname>`) is pre-created by the instructor, so you deploy manifests directly.

Wait for the rollout:

```bash
kubectl rollout status deployment/hello-world
```

Expected output:

```
deployment "hello-world" successfully rolled out
```

---

### Step 4: Verify the Deployment

```bash
kubectl get all
```

Expected output (example):

```
NAME                               READY   STATUS    RESTARTS   AGE
pod/hello-world-85df8f77cb-a7x2k   1/1     Running   0          1m
pod/hello-world-85df8f77cb-m9p3j   1/1     Running   0          1m

NAME                  TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/hello-world   LoadBalancer   10.100.x.x     <pending>     80:3xxxx/TCP   1m

NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-world   2/2     2            2           1m
```

> **Note:** The `EXTERNAL-IP` will show `<pending>` because LoadBalancers are disabled in your namespace quota. This is expected — you will use `port-forward` instead.

---

### Step 5: Access the Application

Since LoadBalancers are restricted, use port-forwarding to reach the service:

```bash
kubectl port-forward svc/hello-world 8080:80
```

In a **separate terminal**, test the application:

```bash
for i in {1..10}; do curl -s http://localhost:8080/; done
```

Expected output — **different pod hostnames** proving load balancing:

```
hello-world from hello-world-85df8f77cb-a7x2k
hello-world from hello-world-85df8f77cb-m9p3j
hello-world from hello-world-85df8f77cb-a7x2k
hello-world from hello-world-85df8f77cb-m9p3j
...
```

> Press `Ctrl+C` in the port-forward terminal when done.

---

### Step 6: Scale the Deployment

Scale up to 4 replicas:

```bash
kubectl scale deployment/hello-world --replicas=4
```

Watch the new pods appear:

```bash
kubectl get pods -w
```

Expected behavior:

```
hello-world-85df8f77cb-a7x2k   1/1     Running   0          5m
hello-world-85df8f77cb-m9p3j   1/1     Running   0          5m
hello-world-85df8f77cb-x9k4r   0/1     Pending   0          0s
hello-world-85df8f77cb-x9k4r   0/1     ContainerCreating   0   1s
hello-world-85df8f77cb-x9k4r   1/1     Running   0          3s
hello-world-85df8f77cb-z2n7w   0/1     Pending   0          0s
hello-world-85df8f77cb-z2n7w   1/1     Running   0          3s
```

Press `Ctrl+C` to stop watching.

Verify 4 pods are running:

```bash
kubectl get pods
```

Scale back down:

```bash
kubectl scale deployment/hello-world --replicas=2
```

---

### Step 7: Demonstrate Self-Healing

Delete one of the running pods to simulate a crash:

```bash
# Get the name of one pod
POD=$(kubectl get pods -o jsonpath='{.items[0].metadata.name}')
echo "Deleting pod: $POD"

# Delete it
kubectl delete pod $POD
```

Immediately watch the recovery:

```bash
kubectl get pods -w
```

Expected behavior:

```
hello-world-85df8f77cb-a7x2k   1/1     Terminating   0          8m
hello-world-85df8f77cb-m9p3j   1/1     Running       0          8m
hello-world-85df8f77cb-q4f8t   0/1     Pending       0          0s
hello-world-85df8f77cb-q4f8t   0/1     ContainerCreating   0   1s
hello-world-85df8f77cb-q4f8t   1/1     Running       0          3s
```

Kubernetes automatically creates a **new pod** to maintain the desired replica count of 2. No human intervention required.

Press `Ctrl+C` to stop watching.

---

### Step 8: Clean Up

Remove all resources from your namespace:

```bash
kubectl delete deployment hello-world
kubectl delete service hello-world
```

Verify the namespace is clean:

```bash
kubectl get all
```

Expected output:

```
No resources found in hw-<yourname> namespace.
```

> **This step is mandatory.** The cluster is shared. Leaving resources running wastes cluster capacity for other students.

---

## Submission

### Deliverable

Create a **PDF document** with the following screenshots. Each screenshot must show the full terminal output including the command you ran.

| # | Screenshot | What It Proves |
|---|-----------|----------------|
| 1 | `kubectl get pods` (empty namespace) | Cluster access works |
| 2 | `kubectl get all` (after deployment) | Deployment created with 2 running pods |
| 3 | `curl` output (10 requests via port-forward) | Load balancing across different pod hostnames |
| 4 | `kubectl get pods` (after scaling to 4) | Horizontal scaling works |
| 5 | `kubectl get pods -w` (after deleting a pod) | Self-healing: new pod replaces deleted one |
| 6 | `kubectl get all` (after cleanup) | Clean namespace, all resources removed |

### Format

- **Filename:** `Homework7_YourName.pdf`
- **Upload to:** eCampus Session 7 Assignment
- **Deadline:** Before Session 8 (15 April 2026)

### Tips

- Include the **full terminal window** in each screenshot (command + output)
- Make sure your **namespace name** (`hw-<yourname>`) is visible in the prompt or output
- Take screenshot 5 **quickly** after deleting the pod — the recovery happens within seconds

---

## Grading Criteria

| Criteria | Points |
|----------|--------|
| Cluster access verified (screenshot 1) | 10 |
| Successful deployment with 2 running pods (screenshot 2) | 20 |
| Load balancing demonstrated with different hostnames (screenshot 3) | 25 |
| Scaling to 4 replicas demonstrated (screenshot 4) | 20 |
| Self-healing demonstrated after pod deletion (screenshot 5) | 15 |
| Cleanup completed, namespace empty (screenshot 6) | 10 |
| **Total** | **100** |

---

## Troubleshooting

### `kubectl` returns "connection refused" or "unauthorized"

- Verify `KUBECONFIG` is set: `echo $KUBECONFIG`
- Verify the file exists: `ls -la $KUBECONFIG`
- If your token has expired, contact the instructor for a new kubeconfig file

### Pods stuck in `Pending` state

```bash
kubectl describe pod <pod-name>
```

Check the Events section. Common causes:
- **Insufficient resources:** The cluster is full. Wait for other students to clean up, or contact the instructor
- **Image pull error:** Check that `ghcr.io/oriolrius/hello-world:v6` is accessible

### `port-forward` drops connection

Port-forwarding can be unstable. If it disconnects, just re-run:

```bash
kubectl port-forward svc/hello-world 8080:80
```

### Deployment shows 0/2 replicas ready

Wait for the readiness probe to pass (up to 15 seconds). If pods keep restarting:

```bash
kubectl logs deployment/hello-world
kubectl describe deployment/hello-world
```

### Deployment YAML fails with "namespace not found"

You are deploying into your pre-created namespace (`hw-<yourname>`), not `hello-world`. The manifests reference `namespace: hello-world` in metadata, but your kubeconfig overrides this. If you get namespace errors, apply with explicit namespace:

```bash
kubectl apply -f k8s/deployment.yaml -n hw-<yourname>
kubectl apply -f k8s/service.yaml -n hw-<yourname>
```

---

## What You Should NOT Do

- **Do not** try to create namespaces — yours is pre-created
- **Do not** try to access other students' namespaces
- **Do not** try to run `kubectl get nodes` — nodes are cluster-scoped and restricted
- **Do not** leave resources running after completing the assignment
- **Do not** deploy images other than `ghcr.io/oriolrius/hello-world`

---

## Resources

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [hello-world repository (v6.x)](https://github.com/oriolrius/hello-world/tree/v6.x)
- [k8s/README.md](../k8s/README.md) — Full Kubernetes deployment guide with advanced operations

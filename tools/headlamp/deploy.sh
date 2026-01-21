#!/bin/bash
# Deploy Headlamp with Basic Auth proxy to EKS
#
# Prerequisites:
#   - kubectl configured for EKS cluster
#   - helm installed
#
# Usage: ./deploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACE="headlamp"

echo "=== Deploying Headlamp to EKS ==="
echo ""

# Step 1: Create namespace
echo "1. Creating namespace..."
kubectl apply -f "$SCRIPT_DIR/namespace.yaml"

# Step 2: Add Headlamp Helm repo
echo "2. Adding Headlamp Helm repository..."
helm repo add headlamp https://kubernetes-sigs.github.io/headlamp/ 2>/dev/null || true
helm repo update

# Step 3: Install Headlamp via Helm
echo "3. Installing Headlamp..."
helm upgrade --install headlamp headlamp/headlamp \
  --namespace "$NAMESPACE" \
  --values "$SCRIPT_DIR/values.yaml" \
  --wait

# Step 4: Create admin user service account
echo "4. Creating admin user..."
kubectl apply -f "$SCRIPT_DIR/admin-user.yaml"

# Step 5: Deploy basic auth proxy
echo "5. Deploying basic auth proxy..."
kubectl apply -f "$SCRIPT_DIR/basic-auth-proxy.yaml"

# Step 6: Wait for deployments
echo "6. Waiting for deployments to be ready..."
kubectl rollout status deployment/headlamp -n "$NAMESPACE"
kubectl rollout status deployment/headlamp-proxy -n "$NAMESPACE"

# Step 7: Get access information
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Getting LoadBalancer URL (may take 1-2 minutes)..."
sleep 10

LB_URL=$(kubectl get svc headlamp-proxy -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
if [ -z "$LB_URL" ]; then
  echo "LoadBalancer URL not ready yet. Check with:"
  echo "  kubectl get svc headlamp-proxy -n $NAMESPACE"
else
  echo ""
  echo "Access Headlamp at: http://$LB_URL:49100"
fi

echo ""
echo "=== Authentication ==="
echo ""
echo "Step 1 - Basic Auth (nginx proxy):"
echo "  Username: admin"
echo "  Password: The2password."
echo ""
echo "Step 2 - Headlamp Token Auth:"
echo "  Get token with: kubectl get secret admin-user-token -n $NAMESPACE -o jsonpath='{.data.token}' | base64 -d"
echo ""

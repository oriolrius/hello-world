#!/bin/bash
# Deploy Headlamp to EKS
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

# Step 5: Wait for deployment
echo "5. Waiting for deployment to be ready..."
kubectl rollout status deployment/headlamp -n "$NAMESPACE"

# Step 6: Get access information
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Getting LoadBalancer URL (may take 1-2 minutes)..."
sleep 10

LB_URL=$(kubectl get svc headlamp -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
if [ -z "$LB_URL" ]; then
  echo "LoadBalancer URL not ready yet. Check with:"
  echo "  kubectl get svc headlamp -n $NAMESPACE"
else
  echo ""
  echo "Access Headlamp at: http://$LB_URL"
fi

echo ""
echo "=== Authentication ==="
echo ""
echo "Get token with:"
echo "  kubectl get secret admin-user-token -n $NAMESPACE -o jsonpath='{.data.token}' | base64 -d"
echo ""
echo "Paste the token in Headlamp's login screen."
echo ""

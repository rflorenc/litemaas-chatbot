# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Open Source Mentor Bot to a Kubernetes or OpenShift cluster.

## Prerequisites

- Kubernetes cluster (1.20+) or OpenShift (4.x+)
- `kubectl` or `oc` CLI configured
- Container image pushed to a registry accessible by the cluster
- LiteMAAS API credentials

## Quick Deploy

```bash
# Create namespace
kubectl create namespace mentor-bot

# Apply all manifests
kubectl apply -f openshift/ -n mentor-bot

# Or using kustomize
kubectl apply -k openshift/ -n mentor-bot
```

## Step-by-Step Deployment

### 1. Build and Push Container Image

First, build and push your container image to a registry:

```bash
# Build
podman build -t registry.example.com/rlteam/mentor-bot:latest .

# Login to registry
podman login registry.example.com

# Push
podman push registry.example.com/rlteam/mentor-bot:latest
```

### 2. Create Namespace

```bash
kubectl create namespace mentor-bot
```

### 3. Create Secrets

Edit `secrets.yaml` and add your base64-encoded credentials:

```bash
# Encode your API key
echo -n "your_api_key_here" | base64

# Apply secrets
kubectl apply -f openshift/secrets.yaml -n mentor-bot
```

### 4. Create ConfigMap

```bash
kubectl apply -f openshift/configmap.yaml -n mentor-bot
```

### 5. Deploy Application

```bash
kubectl apply -f openshift/deployment.yaml -n mentor-bot
```

### 6. Create Service

```bash
kubectl apply -f openshift/service.yaml -n mentor-bot
```

### 7. Create Ingress (Optional)

If you want external access via Ingress:

```bash
kubectl apply -f openshift/ingress.yaml -n mentor-bot
```

## Accessing the Application

### Via Port Forward (Development)

```bash
kubectl port-forward -n mentor-bot svc/mentor-bot-service 8080:8080
```

Then access at: http://localhost:8080

### Via LoadBalancer

```bash
kubectl get service mentor-bot-service -n mentor-bot
```

Get the `EXTERNAL-IP` and access the application.

### Via Ingress

If using Ingress, access at the configured hostname (e.g., http://mentor-bot.example.com)

## Monitoring

### Check Deployment Status

```bash
kubectl get all -n mentor-bot
```

### View Logs

```bash
# View logs from all pods
kubectl logs -n mentor-bot -l app=mentor-bot --tail=100 -f

# View logs from specific pod
kubectl logs -n mentor-bot <pod-name>
```

### Check Pod Status

```bash
kubectl get pods -n mentor-bot
kubectl describe pod -n mentor-bot <pod-name>
```

### Check Events

```bash
kubectl get events -n mentor-bot --sort-by='.lastTimestamp'
```

## Scaling

### Manual Scaling

```bash
kubectl scale deployment mentor-bot -n mentor-bot --replicas=3
```

### Auto-scaling (HPA)

```bash
kubectl apply -f openshift/hpa.yaml -n mentor-bot
```

## Configuration Updates

### Update ConfigMap

```bash
kubectl edit configmap mentor-bot-config -n mentor-bot

# Restart pods to pick up changes
kubectl rollout restart deployment mentor-bot -n mentor-bot
```

### Update Secrets

```bash
kubectl edit secret mentor-bot-secrets -n mentor-bot

# Restart pods
kubectl rollout restart deployment mentor-bot -n mentor-bot
```

### Update Image

```bash
# Set new image
kubectl set image deployment/mentor-bot \
  mentor-bot=registry.example.com/rlteam/mentor-bot:v2 \
  -n mentor-bot

# Check rollout status
kubectl rollout status deployment/mentor-bot -n mentor-bot
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod -n mentor-bot <pod-name>

# Check logs
kubectl logs -n mentor-bot <pod-name>

# Check events
kubectl get events -n mentor-bot
```

### ImagePullBackOff

- Verify image exists in registry
- Check imagePullSecrets if using private registry
- Verify image name and tag

### CrashLoopBackOff

- Check application logs: `kubectl logs -n mentor-bot <pod-name>`
- Verify environment variables and secrets
- Check resource limits

### Service Not Accessible

```bash
# Check service
kubectl get svc -n mentor-bot
kubectl describe svc mentor-bot-service -n mentor-bot

# Check endpoints
kubectl get endpoints -n mentor-bot

# Test from another pod
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n mentor-bot -- \
  curl http://mentor-bot-service:8080/health
```

## OpenShift Specific

### Create Route (Instead of Ingress)

```bash
oc expose svc/mentor-bot-service -n mentor-bot

# Get route URL
oc get route -n mentor-bot
```

### Security Context Constraints

OpenShift applies SCCs automatically. The deployment uses a non-root user (UID 1001) which is compatible with the `restricted` SCC.

### DeploymentConfig (Optional)

You can convert the Deployment to a DeploymentConfig if preferred:

```bash
oc apply -f openshift/openshift/deploymentconfig.yaml -n mentor-bot
```

## Resource Management

### View Resource Usage

```bash
kubectl top pods -n mentor-bot
kubectl top nodes
```

### Adjust Resource Limits

Edit `deployment.yaml` and modify:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "500m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

## Cleanup

### Delete Application

```bash
kubectl delete -f openshift/ -n mentor-bot
```

### Delete Namespace

```bash
kubectl delete namespace mentor-bot
```

## Production Considerations

1. **High Availability**: Set `replicas: 3` in deployment
2. **Resource Limits**: Adjust based on load testing
3. **Persistent Volumes**: Add if storing conversation history
4. **Network Policies**: Implement to restrict traffic
5. **Monitoring**: Integrate with Prometheus/Grafana
6. **Logging**: Ship logs to centralized logging (ELK, Splunk)
7. **Secrets Management**: Use external secrets manager (Vault, Sealed Secrets)
8. **Backup**: Regular backups of ConfigMaps and Secrets
9. **Security Scanning**: Scan images for vulnerabilities

## Manifest Files

- `deployment.yaml` - Main application deployment
- `service.yaml` - ClusterIP service
- `configmap.yaml` - Application configuration
- `secrets.yaml` - Sensitive credentials
- `ingress.yaml` - External access (optional)
- `hpa.yaml` - Horizontal Pod Autoscaler (optional)
- `networkpolicy.yaml` - Network security (optional)

## Support

For issues specific to Kubernetes deployment, consult:
- Main repository: `../../docs/FUTURE_OPENSHIFT.md`
- Kubernetes docs: https://kubernetes.io/docs/
- OpenShift docs: https://docs.openshift.com/

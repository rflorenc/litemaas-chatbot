# Mentor Bot Helm Chart

A Helm chart for deploying the Open Source Mentor Bot on OpenShift and Kubernetes.

## Overview

This Helm chart deploys an AI-powered mentorship chatbot that uses LiteMAAS for intelligent responses. The chart is optimized for OpenShift but works on any Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+ or OpenShift 4.x+
- Helm 3.0+
- LiteMAAS API key
- `oc` or `kubectl` CLI configured

## Installation

### Quick Start (OpenShift)

```bash
# Create namespace
oc new-project mentor-bot

# Install with OpenShift-specific values
helm install mentor-bot ./helm/mentor-bot \
  -f ./helm/mentor-bot/values-openshift.yaml \
  --set secrets.data.LITEMAAS_API_KEY="your-api-key-here"
```

### Standard Kubernetes

```bash
# Create namespace
kubectl create namespace mentor-bot

# Install with default values
helm install mentor-bot ./helm/mentor-bot \
  --namespace mentor-bot \
  --set secrets.data.LITEMAAS_API_KEY="your-api-key-here" \
  --set route.enabled=false \
  --set ingress.enabled=true
```

### Using External Secrets

For production, use external secret management instead of embedding secrets in values:

```bash
# Create secret separately
oc create secret generic mentor-bot-secrets \
  --from-literal=LITEMAAS_API_KEY="your-api-key-here"

# Install without creating secrets
helm install mentor-bot ./helm/mentor-bot \
  -f ./helm/mentor-bot/values-openshift.yaml \
  --set secrets.create=false \
  --set secrets.name=mentor-bot-secrets
```

## Configuration

### Key Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `mentor-bot` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8080` |
| `route.enabled` | Enable OpenShift Route | `true` |
| `ingress.enabled` | Enable Kubernetes Ingress | `false` |
| `secrets.data.LITEMAAS_API_KEY` | LiteMAAS API key | `YOUR_API_KEY_HERE` |

### OpenShift-Specific Configuration

The `values-openshift.yaml` file contains OpenShift-optimized settings:

- Restricted security context compatible with OpenShift SCCs
- OpenShift Route instead of Ingress
- Resource limits adjusted for OpenShift
- OpenShift-specific labels and annotations

### Values Files

- `values.yaml` - Default configuration for all Kubernetes platforms
- `values-openshift.yaml` - OpenShift-specific overrides

To use both:

```bash
helm install mentor-bot ./helm/mentor-bot \
  -f ./helm/mentor-bot/values.yaml \
  -f ./helm/mentor-bot/values-openshift.yaml
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade mentor-bot ./helm/mentor-bot \
  -f ./helm/mentor-bot/values-openshift.yaml \
  --set image.tag=v2.0.0

# Upgrade with new API key
helm upgrade mentor-bot ./helm/mentor-bot \
  --reuse-values \
  --set secrets.data.LITEMAAS_API_KEY="new-api-key"
```

## Uninstalling

```bash
# Uninstall the release
helm uninstall mentor-bot

# Remove namespace (optional)
oc delete project mentor-bot
```

## Examples

### Development Deployment

```bash
helm install mentor-bot-dev ./helm/mentor-bot \
  --set image.tag=dev \
  --set config.flaskEnv=development \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=256Mi
```

### Production with Autoscaling

```bash
helm install mentor-bot-prod ./helm/mentor-bot \
  -f ./helm/mentor-bot/values-openshift.yaml \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=5 \
  --set resources.requests.cpu=500m \
  --set resources.requests.memory=512Mi
```

### Custom Image Registry

```bash
helm install mentor-bot ./helm/mentor-bot \
  --set image.repository=quay.io/myorg/mentor-bot \
  --set image.tag=v1.0.0 \
  --set imagePullSecrets[0].name=quay-credentials
```

## Accessing the Application

### OpenShift Route

```bash
# Get the route URL
export ROUTE_HOST=$(oc get route mentor-bot-route -o jsonpath='{.spec.host}')
echo "Application URL: https://$ROUTE_HOST"

# Test health endpoint
curl https://$ROUTE_HOST/health

# Test chat API
curl -X POST https://$ROUTE_HOST/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hello!"}'
```

### Port Forward (Development)

```bash
kubectl port-forward svc/mentor-bot-service 8080:8080
curl http://localhost:8080/health
```

## Monitoring

```bash
# View logs
kubectl logs -f deployment/mentor-bot

# Watch pods
kubectl get pods -w -l app.kubernetes.io/name=mentor-bot

# Check resource usage
kubectl top pods -l app.kubernetes.io/name=mentor-bot
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod -l app.kubernetes.io/name=mentor-bot

# Check logs
kubectl logs -l app.kubernetes.io/name=mentor-bot --tail=50

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Security Context Issues (OpenShift)

If you encounter security context errors:

```bash
# Check assigned SCC
oc describe pod <pod-name> | grep scc

# Verify service account
oc get sa mentor-bot-sa -o yaml
```

### API Key Issues

```bash
# Verify secret exists
kubectl get secret mentor-bot-secrets

# Check secret data
kubectl get secret mentor-bot-secrets -o jsonpath='{.data.LITEMAAS_API_KEY}' | base64 -d

# Update secret
kubectl create secret generic mentor-bot-secrets \
  --from-literal=LITEMAAS_API_KEY="new-key" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart deployment
kubectl rollout restart deployment/mentor-bot
```

## Advanced Configuration

### Custom ConfigMap

```yaml
config:
  port: "8080"
  flaskEnv: "production"
  litemaasBaseUrl: "https://custom-litemaas.example.com"
  teamSubdomain: "myteam"
```

### Additional Environment Variables

```yaml
extraEnv:
  - name: DEBUG
    value: "true"
  - name: LOG_LEVEL
    value: "INFO"
```

### Custom Volumes

```yaml
extraVolumes:
  - name: custom-config
    configMap:
      name: my-custom-config

extraVolumeMounts:
  - name: custom-config
    mountPath: /etc/custom
    readOnly: true
```

## Security Best Practices

1. **Never commit secrets** - Use external secret management (Vault, Sealed Secrets, etc.)
2. **Use specific image tags** - Avoid `latest` in production
3. **Enable resource limits** - Prevent resource exhaustion
4. **Use restricted SCCs** - Let OpenShift assign appropriate security constraints
5. **Enable TLS** - Always use HTTPS in production via Routes or Ingress

## Contributing

See the main repository for contribution guidelines:
https://github.com/rflorenc/opensourcementor

## Support

For issues and questions:
https://github.com/rflorenc/opensourcementor/issues

## License

See the main repository for license information.

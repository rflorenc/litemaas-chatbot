# Helm-Based OpenShift Deployment

This directory now includes a complete Helm chart for deploying the Open Source Mentor Bot to OpenShift and Kubernetes.

## Directory Structure

```
helm/mentor-bot/
├── Chart.yaml                  # Chart metadata
├── README.md                   # Comprehensive Helm documentation
├── values.yaml                 # Default configuration values
├── values-openshift.yaml       # OpenShift-specific overrides
├── .helmignore                 # Files to ignore when packaging
└── templates/                  # Kubernetes resource templates
    ├── NOTES.txt              # Post-install instructions
    ├── _helpers.tpl           # Template helper functions
    ├── configmap.yaml         # Application configuration
    ├── deployment.yaml        # Main deployment
    ├── hpa.yaml              # Horizontal Pod Autoscaler
    ├── ingress.yaml          # Kubernetes Ingress
    ├── route.yaml            # OpenShift Route
    ├── secret.yaml           # Secrets management
    ├── service.yaml          # Service definition
    └── serviceaccount.yaml   # Service account
```

## Quick Start

### Prerequisites

1. **Helm 3.0+** installed
2. **OpenShift CLI (oc)** logged in to your cluster
3. **LiteMAAS API key** ready

### Option 1: Using Makefile (Recommended)

```bash
# Check Helm installation
make helm-check

# Lint and validate chart
make helm-lint

# Preview what will be deployed
make helm-template

# Install to OpenShift (uses .env for API key)
make helm-install

# Or provide API key explicitly
API_KEY=your-key-here make helm-install
```

### Option 2: Direct Helm Commands

```bash
# Create namespace
oc new-project mentor-bot-rlteam

# Install with OpenShift-specific values
helm install mentor-bot ./helm/mentor-bot \
  -f ./helm/mentor-bot/values-openshift.yaml \
  --set secrets.data.LITEMAAS_API_KEY="your-api-key-here" \
  --namespace mentor-bot-rlteam
```

## Helm vs Direct Deployment Comparison

### Original Deployment (`make oc-deploy`)

**Pros:**
- Simple bash script
- No additional tools needed
- Direct control over resources

**Cons:**
- Manual resource management
- Harder to upgrade/rollback
- No templating or reusability
- Limited configuration management

### Helm Deployment (`make helm-install`)

**Pros:**
- ✅ **Templated Resources** - Reusable across environments
- ✅ **Easy Upgrades** - `helm upgrade` with automatic rollback
- ✅ **Version Control** - Track deployment history
- ✅ **Configuration Management** - Multiple values files
- ✅ **Rollback Support** - One command to rollback
- ✅ **Release Management** - Named releases with metadata
- ✅ **Dry Run** - Test before deploying
- ✅ **Dependency Management** - Chart dependencies

**Cons:**
- Requires Helm installation
- Slightly more complex initially

## Common Operations

### Deploy to OpenShift

```bash
# Check prerequisites
make helm-check

# Install
API_KEY=your-key make helm-install

# Get application URL
make helm-url
```

### Upgrade Deployment

```bash
# Upgrade with new image tag
make helm-upgrade

# Or specify custom values
helm upgrade mentor-bot ./helm/mentor-bot \
  -f ./helm/mentor-bot/values-openshift.yaml \
  --set image.tag=v2.0.0
```

### Monitor Deployment

```bash
# Check status
make helm-status

# View current values
make helm-get-values

# View logs (using oc)
oc logs -f deployment/mentor-bot
```

### Rollback

```bash
# View history
make helm-history

# Rollback to previous version
make helm-rollback

# Or rollback to specific revision
helm rollback mentor-bot 2
```

### Uninstall

```bash
make helm-uninstall
```

## Configuration Options

### Via values.yaml

Edit `helm/mentor-bot/values.yaml` or `values-openshift.yaml`:

```yaml
# Scale replicas
replicaCount: 3

# Use different image
image:
  repository: quay.io/myorg/mentor-bot
  tag: v1.0.0

# Enable autoscaling
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
```

### Via Command Line

```bash
# Set individual values
helm install mentor-bot ./helm/mentor-bot \
  --set replicaCount=3 \
  --set image.tag=v2.0.0 \
  --set secrets.data.LITEMAAS_API_KEY="key"
```

### Via Environment Variables (Makefile)

```bash
# Override defaults
HELM_RELEASE_NAME=my-bot \
HELM_NAMESPACE=production \
API_KEY=your-key \
make helm-install
```

## Advanced Features

### Multiple Environments

```bash
# Development
helm install mentor-bot-dev ./helm/mentor-bot \
  -f values-openshift.yaml \
  --set config.flaskEnv=development \
  --namespace dev

# Production
helm install mentor-bot-prod ./helm/mentor-bot \
  -f values-openshift.yaml \
  -f values-production.yaml \
  --namespace production
```

### External Secrets Management

Instead of storing secrets in Helm values:

```bash
# Create secret externally
oc create secret generic mentor-bot-secrets \
  --from-literal=LITEMAAS_API_KEY="your-key"

# Deploy without creating secrets
helm install mentor-bot ./helm/mentor-bot \
  --set secrets.create=false \
  --set secrets.name=mentor-bot-secrets
```

### Custom Image Registry

```bash
# Use custom registry
helm install mentor-bot ./helm/mentor-bot \
  --set image.repository=quay.io/yourorg/mentor-bot \
  --set image.tag=v1.0.0 \
  --set imagePullSecrets[0].name=quay-credentials
```

## Makefile Helm Targets

All available Helm commands via Makefile:

```bash
# Help
make helm-help              # Show detailed help

# Chart Management
make helm-check             # Verify Helm installation
make helm-lint              # Validate chart
make helm-template          # Render templates
make helm-package           # Package chart

# Deployment
make helm-install           # Install chart
make helm-upgrade           # Upgrade release
make helm-uninstall         # Remove release

# Monitoring
make helm-list              # List releases
make helm-status            # Show status
make helm-get-values        # Show values
make helm-history           # Show history
make helm-url               # Get application URL

# Development
make helm-debug             # Debug mode
make helm-rollback          # Rollback
```

## Migration from Direct Deployment

If you already deployed using `make oc-deploy`, you can:

### Option 1: Keep Both

The Helm deployment uses different resource names, so they won't conflict. You can run both side-by-side in different namespaces.

### Option 2: Migrate to Helm

```bash
# Clean up old deployment
make oc-clean

# Deploy with Helm
make helm-install
```

### Option 3: Adopt Existing Resources

Helm can adopt existing resources (advanced):

```bash
# Label existing resources
oc label deployment/mentor-bot app.kubernetes.io/managed-by=Helm

# Create Helm release metadata
helm install mentor-bot ./helm/mentor-bot \
  --adopt \
  --existing-resources
```

## Troubleshooting

### Chart Validation Errors

```bash
# Lint chart
make helm-lint

# Debug template rendering
make helm-debug
```

### Deployment Issues

```bash
# Check status
make helm-status

# View resources
oc get all -l app.kubernetes.io/name=mentor-bot

# Check logs
oc logs deployment/mentor-bot
```

### API Key Issues

```bash
# Verify secret
oc get secret mentor-bot-secrets -o yaml

# Update secret
oc create secret generic mentor-bot-secrets \
  --from-literal=LITEMAAS_API_KEY="new-key" \
  --dry-run=client -o yaml | oc apply -f -

# Restart deployment
oc rollout restart deployment/mentor-bot
```

## Best Practices

1. **Version Control** - Store Helm charts in Git
2. **Values Files** - Use separate values files per environment
3. **External Secrets** - Don't store secrets in values.yaml
4. **Image Tags** - Use specific tags, not `latest`
5. **Resource Limits** - Always set resource requests/limits
6. **Dry Run** - Test with `--dry-run` before deployment
7. **Rollback Plan** - Test rollback process before production

## Documentation

- **Chart README**: `helm/mentor-bot/README.md` - Comprehensive Helm documentation
- **Chart Values**: `helm/mentor-bot/values.yaml` - All configurable options
- **OpenShift Values**: `helm/mentor-bot/values-openshift.yaml` - OpenShift-specific settings
- **Post-Install Notes**: Displayed after installation with helpful commands

## Comparison Matrix

| Feature | `make oc-deploy` | `make helm-install` |
|---------|------------------|---------------------|
| Installation | ✅ Simple | ✅ Simple |
| Upgrades | ⚠️ Manual | ✅ Automated |
| Rollbacks | ❌ Manual | ✅ One command |
| Configuration | ⚠️ Script vars | ✅ Values files |
| Templating | ❌ Static YAML | ✅ Templated |
| Multi-env | ⚠️ Duplicate files | ✅ Values files |
| Version Control | ⚠️ Limited | ✅ Full history |
| Dependencies | ❌ None | ✅ Chart deps |
| Testing | ⚠️ Manual | ✅ Helm tests |
| Dry Run | ❌ No | ✅ Yes |

## Next Steps

1. **Try Helm Deployment**
   ```bash
   make helm-check
   API_KEY=your-key make helm-install
   ```

2. **Customize Values**
   - Edit `values-openshift.yaml`
   - Add environment-specific values

3. **Set Up CI/CD**
   - Use Helm in your pipeline
   - Automate deployments

4. **Explore Advanced Features**
   - Chart dependencies
   - Helm hooks
   - Chart testing

## Support

For issues or questions:
- GitHub Issues: https://github.com/rflorenc/opensourcementor/issues
- Chart Documentation: `helm/mentor-bot/README.md`

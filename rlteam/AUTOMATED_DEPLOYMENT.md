# Automated OpenShift Deployment

The `make oc-deploy` command now automatically uses configuration from your `.env` file, making deployment fully automated!

## 🚀 Quick Start

### Automated Deployment (No Prompts!)

```bash
# Ensure .env file has the API key
cat .env | grep LITEMAAS_API_KEY

# Deploy with one command - uses .env automatically!
make oc-deploy
```

That's it! The deployment will:
1. ✅ Read `LITEMAAS_API_KEY` from `.env`
2. ✅ Use default project: `mentor-bot-rlteam`
3. ✅ Use default build strategy: BuildConfig (1)
4. ✅ Deploy everything automatically

### What Gets Automated

The `make oc-deploy` command now reads from `.env`:

| Variable | Source | Default |
|----------|--------|---------|
| `LITEMAAS_API_KEY` | `.env` | **Required** |
| `OC_PROJECT` | `.env` (optional) | `mentor-bot-rlteam` |
| `BUILD_STRATEGY` | Environment | `1` (BuildConfig) |

## 📋 Usage Examples

### 1. Simple Automated Deployment

```bash
# Uses all defaults from .env
make oc-deploy
```

**What happens:**
- ✅ Reads API key from `.env`
- ✅ Creates project `mentor-bot-rlteam`
- ✅ Builds image in cluster (BuildConfig)
- ✅ Deploys application
- ✅ Creates route

### 2. Custom Build Strategy

```bash
# Use a different build strategy
BUILD_STRATEGY=2 make oc-deploy  # Push from local
BUILD_STRATEGY=3 make oc-deploy  # Skip build, use existing
```

### 3. Custom Project Name

Add to your `.env` file:
```bash
OC_PROJECT=my-custom-project
```

Then deploy:
```bash
make oc-deploy
```

### 4. Override Everything

```bash
OC_PROJECT=test-project BUILD_STRATEGY=3 make oc-deploy
```

## 🔧 Build Strategies Explained

### Strategy 1: BuildConfig (Default) ⭐
**Best for:** Daily development

```bash
make oc-deploy  # Default uses Strategy 1
```

- Builds image **inside OpenShift**
- Fast and reliable
- No network upload needed
- Uses OpenShift-compatible Containerfile

### Strategy 2: Internal Registry
**Best for:** Testing locally first

```bash
BUILD_STRATEGY=2 make oc-deploy
```

- Builds locally with Podman
- Pushes to OpenShift registry
- Full control over build

### Strategy 3: Skip Build
**Best for:** Config changes only

```bash
BUILD_STRATEGY=3 make oc-deploy
```

- No build, uses existing image
- Fastest deployment
- Perfect when only changing ConfigMap/Secrets

## 📝 Environment Variables Reference

### Required in .env
```bash
# Required
LITEMAAS_API_KEY=REPLACE_ME
```

### Optional in .env
```bash
# Optional - use custom project name
OC_PROJECT=mentor-bot-rlteam

# Optional - override at runtime
# BUILD_STRATEGY=1  # Don't put in .env, use at command line
```

## 🎯 Common Workflows

### First Deployment
```bash
# 1. Verify .env has API key
cat .env | grep LITEMAAS_API_KEY

# 2. Check OpenShift login
make oc-check

# 3. Deploy!
make oc-deploy
```

### Code Changes - Rebuild
```bash
# Quick rebuild (doesn't redeploy everything)
make oc-build

# Full rebuild (clean + deploy)
make oc-rebuild
```

### Config Changes Only
```bash
# Edit ConfigMap
vim openshift/configmap.yaml

# Deploy without rebuilding image
BUILD_STRATEGY=3 make oc-deploy

# Or just apply the config
oc apply -f openshift/configmap.yaml
oc rollout restart deployment/mentor-bot
```

### Fix SCC Issue
```bash
# Delete failing deployment
oc delete deployment mentor-bot

# Deploy with OpenShift-compatible files
BUILD_STRATEGY=1 make oc-deploy
```

## 🔍 Verification

After deployment, verify everything:

```bash
# Quick check
make oc-status

# Full verification
make oc-verify

# Get application URL
make oc-url

# View logs
make oc-logs
```

## 🛠 Troubleshooting

### API Key Not Found

```bash
❌ LITEMAAS_API_KEY not set in .env file.
```

**Solution:**
```bash
# Check .env file
cat .env | grep LITEMAAS_API_KEY

# If missing, add it
echo 'LITEMAAS_API_KEY=REPLACE_ME' >> .env
```

### Not Logged into OpenShift

```bash
❌ Not logged into OpenShift. Run: oc login
```

**Solution:**
```bash
oc login <your-cluster-url>
# Then retry
make oc-deploy
```

### Build Failed

```bash
# Check build logs
oc logs -f bc/mentor-bot

# Rebuild
make oc-build

# Or clean and restart
make oc-rebuild
```

### SCC Error (UID not in range)

```bash
# Use OpenShift-specific deployment
oc delete deployment mentor-bot
make oc-deploy  # Uses OpenShift-compatible files
```

See `OPENSHIFT_SCC_FIX.md` for details.

## 📚 Manual Alternative

If you prefer interactive prompts:

```bash
# Run script directly (will prompt for inputs)
./openshift-deploy.sh
```

Or set environment variables:

```bash
OC_PROJECT=my-project \
LITEMAAS_API_KEY=sk-xxx \
BUILD_STRATEGY=1 \
./openshift-deploy.sh
```

## 🎓 Advanced Usage

### Deploy to Multiple Projects

```bash
# Deploy to dev
OC_PROJECT=mentor-bot-dev make oc-deploy

# Deploy to staging
OC_PROJECT=mentor-bot-staging make oc-deploy

# Deploy to prod (use existing image)
OC_PROJECT=mentor-bot-prod BUILD_STRATEGY=3 make oc-deploy
```

### CI/CD Integration

```bash
#!/bin/bash
# deploy-to-openshift.sh

# Load environment
source .env

# Login to OpenShift
oc login --token=$OC_TOKEN --server=$OC_SERVER

# Deploy
BUILD_STRATEGY=1 make oc-deploy

# Verify
make oc-verify
```

### Quick Rollback

```bash
# Scale to 0
make oc-scale N=0

# Redeploy previous version
oc rollout undo deployment/mentor-bot

# Scale back up
make oc-scale N=1
```

## 📊 Complete Command Reference

```bash
# Prerequisites
make oc-check              # Verify login and setup

# Deployment
make oc-deploy             # Deploy (automated)
make oc-build              # Rebuild image
make oc-rebuild            # Clean + redeploy

# Monitoring
make oc-status             # Show all resources
make oc-logs               # Follow logs
make oc-url                # Get application URL
make oc-verify             # Full verification

# Management
make oc-restart            # Restart deployment
make oc-scale N=3          # Scale replicas
make oc-shell              # Open shell in pod
make oc-clean              # Delete resources

# Help
make oc-help               # Show detailed help
```

## ✅ Benefits of Automated Deployment

1. **No Manual Input**: API key read from `.env`
2. **Consistent**: Same deployment every time
3. **Fast**: One command to deploy
4. **Safe**: Validates `.env` before starting
5. **Flexible**: Override with environment variables
6. **CI/CD Ready**: Perfect for automation

## 🔐 Security Note

**Never commit `.env` to git!**

```bash
# Already in .gitignore:
.env
*.env
!.env.template
```

Always use `.env.template` as the example and keep actual credentials in `.env` locally only.

---

**Ready to Deploy?**

```bash
make oc-deploy
```

That's it! 🚀

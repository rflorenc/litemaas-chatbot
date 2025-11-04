# OpenShift Image Build Strategies

This document explains the three different image build strategies available when deploying to OpenShift.

## Strategy 1: OpenShift BuildConfig (Recommended) ✅

**How it works:**
1. Creates a BuildConfig resource in OpenShift
2. Uploads your source code from local directory to OpenShift
3. OpenShift builds the container image **inside the cluster**
4. Stores the image in OpenShift's internal ImageStream
5. Deployment automatically references the ImageStream

**Advantages:**
- ✅ No need to push large images over network
- ✅ Builds happen in the cluster (faster, more reliable)
- ✅ Automatic rebuilds with `make oc-build`
- ✅ Image stays in cluster registry
- ✅ Works with CI/CD pipelines

**What happens:**
```bash
# Creates BuildConfig
oc new-build --name=mentor-bot --binary --strategy=docker

# Uploads local source and builds
oc start-build mentor-bot --from-dir=. --follow

# Creates ImageStream: mentor-bot:latest
# Deployment references: image: mentor-bot:latest
```

**When to use:**
- **Default choice** - works in most scenarios
- When you have a good network connection to OpenShift
- For continuous development/testing
- When you want automatic builds on code changes

**Build Process:**
```
Local Source → Upload to OpenShift → Build in Cluster → ImageStream → Deployment
```

---

## Strategy 2: OpenShift Internal Registry (Push from Local)

**How it works:**
1. Builds the container image **locally** using Podman
2. Tags the image for OpenShift's internal registry
3. Logs into OpenShift registry with your credentials
4. Pushes the built image to OpenShift registry
5. Deployment references the pushed image

**Advantages:**
- ✅ Full control over build process locally
- ✅ Can test image locally before pushing
- ✅ No BuildConfig needed
- ✅ Works when BuildConfig has issues

**What happens:**
```bash
# Build locally
podman build -t mentor-bot:latest .

# Get OpenShift registry URL
REGISTRY="image-registry.openshift-image-registry.svc:5000"

# Tag for OpenShift
podman tag mentor-bot:latest \
  $REGISTRY/mentor-bot-rlteam/mentor-bot:latest

# Login to OpenShift registry
podman login -u $(oc whoami) -p $(oc whoami -t) $REGISTRY

# Push to OpenShift
podman push $REGISTRY/mentor-bot-rlteam/mentor-bot:latest

# Deployment references:
# image: image-registry.openshift-image-registry.svc:5000/mentor-bot-rlteam/mentor-bot:latest
```

**When to use:**
- When you want to build locally first
- When you have slow network to OpenShift (build locally once, push)
- When BuildConfig fails or has issues
- When you want to test the exact image before pushing

**Build Process:**
```
Build Locally → Tag → Push to OpenShift Registry → Deployment
```

---

## Strategy 3: Skip Image Build (Use Existing Image)

**How it works:**
1. Assumes an image **already exists** somewhere
2. Doesn't build anything new
3. Deployment references an existing image location
4. Image can be from:
   - Previous BuildConfig (ImageStream already exists)
   - OpenShift registry (already pushed)
   - External registry (Quay.io, Docker Hub, etc.)

**Advantages:**
- ✅ Fastest deployment (no build time)
- ✅ Uses exact same image across environments
- ✅ Ideal for promoting between environments
- ✅ Good for testing K8s manifests without rebuilding

**When to use:**

### Scenario A: Redeploying After Changes to K8s Manifests
```bash
# You already deployed once with Strategy 1 or 2
# Now you changed deployment.yaml, configmap.yaml, etc.
# You don't need to rebuild the image

# Choose Strategy 3
# Deployment will reference: mentor-bot:latest (existing ImageStream)
```

### Scenario B: Using External Registry Image
```bash
# You pushed to Quay.io or Docker Hub
podman build -t quay.io/yourorg/mentor-bot:v1.0 .
podman push quay.io/yourorg/mentor-bot:v1.0

# Then manually update openshift/deployment.yaml:
# image: quay.io/yourorg/mentor-bot:v1.0

# Choose Strategy 3
```

### Scenario C: Promoting Between Environments
```bash
# Dev environment built the image
# You want to deploy the SAME image to staging

# In staging cluster:
# Choose Strategy 3
# Image: dev-registry/mentor-bot:v1.0 (from dev)
```

**What the deployment does:**
```yaml
# In openshift/deployment.yaml, the image field is used as-is:

# If using ImageStream (from previous BuildConfig):
image: mentor-bot:latest

# If using external registry:
image: quay.io/yourorg/mentor-bot:v1.0

# If using OpenShift internal registry:
image: image-registry.openshift-image-registry.svc:5000/mentor-bot-rlteam/mentor-bot:latest
```

**When to use:**
- Redeploying after changing only K8s manifests
- Testing configuration changes without rebuilding
- Using pre-built images from external registry
- Promoting exact image between environments (dev → staging → prod)
- Quick rollouts when image is already available

**Process:**
```
No Build → Use Existing Image Reference → Deployment
```

---

## Comparison Table

| Feature | BuildConfig | Internal Registry | Skip Build |
|---------|------------|-------------------|------------|
| Build Location | In cluster | Locally | N/A |
| Network Upload | Source code | Full image | None |
| Build Time | ~2-5 min | ~2-5 min | 0 sec |
| Rebuild | `make oc-build` | Rebuild + push | Use new image |
| Image Location | ImageStream | Registry | Wherever it is |
| Best For | Development | Local testing | Redeployment |

---

## How to Choose

```
┌─────────────────────────────────────┐
│ Do you have an image already built? │
└──────────┬──────────────────────────┘
           │
           ├─ YES ──→ Strategy 3: Skip Build
           │          (fastest, no build time)
           │
           └─ NO ───→ Do you want to build locally or in cluster?
                      │
                      ├─ In Cluster ──→ Strategy 1: BuildConfig (recommended)
                      │                 (automatic, integrated)
                      │
                      └─ Locally ─────→ Strategy 2: Internal Registry
                                        (full control, test locally)
```

---

## Practical Examples

### Example 1: First-Time Deployment
```bash
# Use Strategy 1 (BuildConfig)
make oc-deploy
# Choose: 1

# Result: Image built in cluster, stored in ImageStream
```

### Example 2: Changed Code, Need to Rebuild
```bash
# Use make oc-build (uses existing BuildConfig)
make oc-build

# Or full rebuild:
make oc-rebuild
```

### Example 3: Changed Only ConfigMap
```bash
# Image doesn't need rebuilding
# Use Strategy 3

# Option A: Just apply the change
oc apply -f openshift/configmap.yaml
oc rollout restart deployment/mentor-bot

# Option B: Use deployment script with Strategy 3
make oc-deploy
# Choose: 3
```

### Example 4: Building Locally to Test
```bash
# Build and test locally first
podman build -t mentor-bot:latest .
podman run -p 8080:8080 --env-file .env mentor-bot:latest
# Test at localhost:8080

# Then push to OpenShift with Strategy 2
make oc-deploy
# Choose: 2
```

### Example 5: Using Quay.io Registry
```bash
# Build and push to Quay.io
podman build -t quay.io/yourorg/mentor-bot:v1.0 .
podman login quay.io
podman push quay.io/yourorg/mentor-bot:v1.0

# Update openshift/deployment.yaml
sed -i 's|image: mentor-bot:latest|image: quay.io/yourorg/mentor-bot:v1.0|' openshift/deployment.yaml

# Deploy with Strategy 3
make oc-deploy
# Choose: 3
```

---

## Current Deployment Image Reference

Your current `openshift/deployment.yaml` has:

```yaml
image: mentor-bot:latest
```

This means:
- **Strategy 1**: Will reference the ImageStream created by BuildConfig
- **Strategy 2**: Script updates this to point to internal registry
- **Strategy 3**: Uses this as-is (must exist)

---

## Troubleshooting

### "Image not found" with Strategy 3
```bash
# Check if ImageStream exists
oc get is

# If not, you need to build first (Strategy 1 or 2)
```

### BuildConfig Fails
```bash
# Fall back to Strategy 2
make oc-deploy
# Choose: 2
```

### Want to Change Strategy
```bash
# Clean and rebuild
make oc-clean
make oc-deploy
# Choose different strategy
```

---

## Recommendations

**For Development**: Strategy 1 (BuildConfig)
- Quick iterations
- Automatic builds
- `make oc-build` for rebuilds

**For Testing**: Strategy 2 (Internal Registry)
- Test locally first
- Push when ready
- Full control

**For Production**: Strategy 3 (External Registry)
- Pre-built, tested images
- Version tags (v1.0, v1.1)
- Immutable deployments

**For Quick Config Changes**: Strategy 3 (Skip Build)
- No code changes
- Only manifest updates
- Fastest deployment

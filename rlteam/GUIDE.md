# 🧭 Team rlteam — Configuration & Remote Access Guide

Welcome to the Open Source Mentor Bot development workspace! This guide will help you set up, develop, and deploy your chatbot in an isolated container environment.

---

## 📁 Folder & Workspace

Work exclusively in:
```
/srv/containers/rlteam
```

Or locally:
```
opensourcementor/teams/rlteam/
```

Each service component lives under this folder with a clear structure.

---

## 🗂️ Registry & Image Namespace

Your team's container registry namespace:
```
registry.<IP>.sslip.io/rlteam
```

### Manual Build & Push (Optional)

```bash
# Build locally
podman build -t registry.<IP>.sslip.io/rlteam/mentor-bot:latest .

# Push to registry
podman push --tls-verify=false registry.<IP>.sslip.io/rlteam/mentor-bot:latest
```

**Note**: `podman-compose build` builds locally by default. Pushing to registry is only needed for shared deployments or Kubernetes.

---

## ⚙️ Environment Configuration

### Step 1: Create .env File

```bash
# Copy template
cp .env.template .env

# Edit with your values
vim .env  # or nano, or your preferred editor
```

### Step 2: Required Configuration

Update these values in `.env`:

```dotenv
# Registry Configuration
REGISTRY_HOST=registry.192.168.1.100.sslip.io  # Replace <IP>
REGISTRY_NAMESPACE=rlteam
IMAGE_NAME=mentor-bot
TAG=latest

# Routing Configuration
TEAM_SUBDOMAIN=rlteam
HOST_SUFFIX=192.168.1.100.sslip.io  # Replace <IP>

# Application
PORT=8080
FLASK_ENV=production

# LiteMAAS API (IMPORTANT: Get your key from hackathon organizers)
LITEMAAS_BASE_URL=https://lite-maas.example/api
LITEMAAS_API_KEY=your_actual_api_key_here
```

**⚠️ CRITICAL**: Replace placeholders with actual values:
- `<IP>` → Actual IP address from organizers
- `your_actual_api_key_here` → Your LiteMAAS API key

---

## 🚀 Build & Deploy Workflow

### Quick Start (Recommended)

```bash
# One-command setup
make setup

# Edit .env with your credentials
vim .env

# Build and run
make build-run
```

### Step-by-Step

#### 1. Initial Setup

```bash
# Create Python venv and install dependencies
make setup

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Build Container

```bash
# Using Makefile
make build

# Or manually with podman-compose
podman-compose build

# Or direct podman build
podman build -t mentor-bot:latest .
```

#### 3. Login to Registry (Optional)

```bash
# Using Makefile
make login

# Or manually
podman login registry.<IP>.sslip.io
```

#### 4. Start Application

```bash
# Using Makefile
make up

# Or manually
podman-compose up -d

# View logs
make logs
```

#### 5. Access Application

**Local Access:**
```
http://localhost:8080
```

**Traefik Routing (if configured):**
```
http://rlteam.<IP>.sslip.io
```

**Health Check:**
```bash
curl http://localhost:8080/health
```

---

## 🌐 Remote Access (MiniCloud Setup)

If you're developing on a remote MiniCloud server, follow these steps:

### 1. SSH Key Setup

Provide your public SSH key to the hackathon host:

```bash
# Generate key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Display your public key
cat ~/.ssh/id_ed25519.pub
```

Send this public key to the organizers for the `rlteam` user.

### 2. SSH Connection

```bash
# SSH into MiniCloud (port 30022)
ssh -p 30022 -i ~/.ssh/id_ed25519 rlteam@<MINICLOUD_HOST>
```

### 3. Navigate to Workspace

```bash
cd /srv/containers/rlteam
ls -la  # Verify your files
```

### 4. Development Workflow

```bash
# Build and run
podman-compose build
podman-compose up -d

# Check status
podman ps

# View logs
podman-compose logs -f

# Stop
podman-compose down
```

### 5. File Transfer (SCP)

```bash
# Upload local file to remote
scp -P 30022 ./localfile rlteam@<MINICLOUD_HOST>:/srv/containers/rlteam/

# Download remote file to local
scp -P 30022 rlteam@<MINICLOUD_HOST>:/srv/containers/rlteam/remotefile ./

# Upload entire directory
scp -P 30022 -r ./app/ rlteam@<MINICLOUD_HOST>:/srv/containers/rlteam/
```

### 6. Local Port Forwarding (Optional)

If Traefik routing is not working, use SSH port forwarding:

```bash
# Forward remote port 8080 to local port 8080
ssh -p 30022 -i ~/.ssh/id_ed25519 -L 8080:127.0.0.1:8080 rlteam@<MINICLOUD_HOST>

# Then access locally at:
# http://localhost:8080
```

---

## 🧠 Quick Debugging Commands

| Action | Command |
|--------|---------|
| **Check running containers** | `podman ps` |
| **View logs** | `podman-compose logs -f` |
| **Restart application** | `podman-compose restart` |
| **Stop application** | `podman-compose down` |
| **Rebuild without cache** | `podman-compose build --no-cache` |
| **Open shell in container** | `podman exec -it rlteam-mentor-bot /bin/bash` |
| **Check health** | `curl http://localhost:8080/health` |
| **View environment** | `podman exec rlteam-mentor-bot env` |
| **Check disk usage** | `podman system df` |
| **Prune unused resources** | `podman system prune` |

---

## 🐛 Troubleshooting

### Container Won't Start

**Problem**: Container exits immediately or fails to start.

**Solutions**:
```bash
# Check logs for errors
podman logs rlteam-mentor-bot

# Verify .env file exists
ls -la .env

# Check environment variables
podman exec rlteam-mentor-bot env | grep LITEMAAS

# Rebuild from scratch
make clean
make build-run
```

### Port Already in Use

**Problem**: "Port 8080 is already allocated"

**Solutions**:
```bash
# Find process using port
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Stop conflicting container
podman stop $(podman ps -q --filter "publish=8080")

# Change port in .env
PORT=8081
```

### LiteMAAS Connection Errors

**Problem**: "Failed to connect to LiteMAAS"

**Solutions**:
```bash
# Verify API key is set
echo $LITEMAAS_API_KEY

# Test connectivity
curl -H "Authorization: Bearer $LITEMAAS_API_KEY" \
     $LITEMAAS_BASE_URL/v1/models

# Check container can reach external network
podman exec rlteam-mentor-bot ping -c 3 8.8.8.8
```

### Permission Denied Errors

**Problem**: "Permission denied" when building or running.

**Solutions**:
```bash
# SELinux context (RHEL/Fedora)
chcon -R -t container_file_t .

# File permissions
chmod +x run.py
chmod -R 755 app/

# Podman rootless
podman system migrate
```

### Image Build Fails

**Problem**: Build fails with dependency errors.

**Solutions**:
```bash
# Clean build cache
podman system prune -a

# Build with no cache
podman build --no-cache -t mentor-bot:latest .

# Check Containerfile syntax
podman build --pull -t mentor-bot:latest .
```

---

## 🧪 Development Tips

### Local Development (Python venv)

For faster iteration without rebuilding containers:

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server with hot reload
make dev

# Or manually:
export $(cat .env | xargs)
python run.py
```

### Testing Changes

```bash
# Run unit tests
make test

# Run specific test
podman exec rlteam-mentor-bot pytest tests/test_utils.py -v

# Run with coverage
podman exec rlteam-mentor-bot pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Fix common issues automatically
podman exec rlteam-mentor-bot black app/
podman exec rlteam-mentor-bot flake8 app/ --max-line-length=100
```

---

## 📊 Monitoring & Logs

### Container Logs

```bash
# Follow logs in real-time
make logs

# View last 50 lines
podman logs --tail 50 rlteam-mentor-bot

# View logs with timestamps
podman logs -t rlteam-mentor-bot

# Filter logs by level
podman logs rlteam-mentor-bot 2>&1 | grep ERROR
```

### Health Monitoring

```bash
# Check health status
make health

# Watch health continuously (every 5s)
watch -n 5 'curl -s http://localhost:8080/health | python3 -m json.tool'

# Check resource usage
podman stats rlteam-mentor-bot
```

---

## ❤️ Red Hat Values Reminder

As you develop, remember Red Hat's core values:

- **🌐 Open Collaboration**: Share your learnings with teammates
- **🔍 Transparency**: Document your decisions in code and commits
- **🤖 Automation**: Use the Makefile to automate repetitive tasks
- **👥 Community First**: Help others when they're stuck
- **🤝 Trust**: Build reliable software through testing and validation

---

## 🎯 Hackathon Deliverables Checklist

- [ ] `.env` file configured with LiteMAAS credentials
- [ ] Container builds successfully
- [ ] Application accessible via browser
- [ ] Health endpoint returns 200 OK
- [ ] Chat functionality works with LiteMAAS
- [ ] Code follows input sanitization best practices
- [ ] README documents architecture and decisions
- [ ] Tests pass successfully
- [ ] Container pushed to registry (optional)

---

## 📚 Additional Resources

### Main Repository Documentation
- `../../docs/QUICKSTART_PODMAN.md` - Podman basics
- `../../docs/CHEATSHEET_PODMAN.md` - Command reference
- `../../docs/LITEMAAS_REFERENCE.md` - LiteMAAS API details
- `../../docs/SECURITY_BEST_PRACTICES.md` - Security guidelines
- `../../docs/TROUBLESHOOTING.md` - Common issues

### Makefile Commands
```bash
make help  # Show all available commands
```

### Project Structure
See `README.md` for detailed file structure and component descriptions.

---

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**: `make logs`
2. **Health Check**: `make health`
3. **Review Documentation**: See links above
4. **Ask Organizers**: Reach out via Slack/email
5. **Collaborate**: Help teammates and learn together

---

Happy hacking! Remember: focus on learning, not just completion. The setup is designed to teach you how containers, APIs, and routing work together in a real-world scenario.

**Built with ❤️ for the Red Hat Open Source Hackathon**

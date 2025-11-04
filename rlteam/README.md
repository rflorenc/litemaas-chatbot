# 🤖 Open Source Mentor Bot

A containerized chatbot built for the Red Hat Open Source Hackathon that helps beginners learn about open source software, Red Hat values, and community collaboration.

## 🎯 Purpose

This demo application showcases:
- **Containerization with Podman**: Production-ready containers using Red Hat UBI
- **LiteMAAS Integration**: Llama-4-Scout-17B LLM for intelligent responses
- **Red Hat Values**: Open collaboration, transparency, community-first principles
- **Modern Python Stack**: Flask, gunicorn, proper security practices

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   Traefik   │ (Optional - for routing)
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│   Flask Application     │
│   - Web UI (/)          │
│   - Chat API (/api/chat)│
│   - Health (/health)    │
└──────┬──────────────────┘
       │ HTTPS + API Key
       ▼
┌─────────────┐
│  LiteMAAS   │ (Llama-4-Scout-17B)
└─────────────┘
```

**Key Components:**
- **Flask**: Lightweight web framework serving UI and API
- **Gunicorn**: Production WSGI server (2 workers, 4 threads)
- **LiteMAAS Client**: HTTP client for LLM completions
- **Input Sanitization**: Protection against prompt injection attacks

## 🚀 Quick Start

### Prerequisites
- Podman or Docker installed
- LiteMAAS API credentials
- Python 3.11+ (for local development)

### 1. Initial Setup

```bash
# Clone and navigate to the project
cd teams/rlteam

# Create environment configuration
make setup

# Edit .env with your credentials
vim .env  # Add your LITEMAAS_API_KEY
```

### 2. Build and Run

```bash
# Build the container image
make build

# Start the application
make up

# View logs
make logs
```

### 3. Access the Application

- **Local**: http://localhost:8080
- **Traefik**: http://rlteam.<IP>.sslip.io (if configured)
- **Health Check**: http://localhost:8080/health

## 📝 Environment Variables

Required variables in `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `REGISTRY_HOST` | Container registry host | `registry.192.168.1.100.sslip.io` |
| `REGISTRY_NAMESPACE` | Your team namespace | `rlteam` |
| `IMAGE_NAME` | Container image name | `mentor-bot` |
| `TAG` | Image tag | `latest` |
| `TEAM_SUBDOMAIN` | Your subdomain | `rlteam` |
| `HOST_SUFFIX` | Domain suffix | `192.168.1.100.sslip.io` |
| `PORT` | Application port | `8080` |
| `LITEMAAS_BASE_URL` | LiteMAAS API endpoint | `https://lite-maas.example/api` |
| `LITEMAAS_API_KEY` | LiteMAAS API key | `your_api_key_here` |

## 🛠️ Development

### Local Development (Python venv)

```bash
# Create virtual environment and install dependencies
make venv
make install

# Run development server (with hot reload)
make dev
```

### Container Development

```bash
# Build and run with logs
make build-run

# Open shell in running container
make shell

# Run tests
make test

# Format code
make format

# Run linters
make lint
```

## 🐛 Debugging

### Check Container Status
```bash
podman ps
podman logs rlteam-mentor-bot
```

### Health Check
```bash
make health
# or
curl http://localhost:8080/health
```

### Common Issues

**Container won't start:**
- Check `.env` file exists and has all required variables
- Verify port 8080 is not already in use
- Check logs: `make logs`

**LiteMAAS errors:**
- Verify `LITEMAAS_API_KEY` is correct
- Check `LITEMAAS_BASE_URL` is accessible
- Review API logs in container logs

**Permission issues:**
- Ensure SELinux context is correct (Podman on RHEL/Fedora)
- Verify user has permission to run containers

## 📋 API Endpoints

### `GET /`
Web UI interface for chatting with the bot.

### `POST /api/chat`
Chat API endpoint for programmatic access.

**Request:**
```json
{
  "message": "What are Red Hat's core values?"
}
```

**Response:**
```json
{
  "response": "Red Hat's core values include...",
  "status": "success"
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "open-source-mentor-bot",
  "version": "1.0.0"
}
```

## 🔒 Security Features

- **Input Sanitization**: Removes HTML, limits length, prevents prompt injection
- **Non-root User**: Container runs as UID 1001 (Red Hat best practice)
- **API Key Protection**: Environment-based secrets, never in code
- **Request Validation**: Strict payload validation
- **Production WSGI**: Gunicorn with controlled workers/threads

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test file
podman exec rlteam-mentor-bot pytest tests/test_utils.py -v

# Run with coverage
podman exec rlteam-mentor-bot pytest --cov=app tests/
```

## 📦 Deployment

### Container Registry

```bash
# Login to registry
make login

# Push image
make push
```

### Kubernetes/OpenShift

```bash
# Apply manifests
kubectl apply -f openshift/

# Or using kustomize
kubectl apply -k openshift/
```

See [openshift/README.md](openshift/README.md) for detailed Kubernetes deployment instructions.

## 🎓 Learning Resources

Built-in knowledge areas:
- Open source best practices
- Red Hat values and culture
- Containerization with Podman
- Community collaboration
- Getting started with contributions

## 🤝 Red Hat Values

This project embodies Red Hat's core values:

- **🌐 Open Collaboration**: Work together transparently
- **🔍 Transparency**: Share knowledge and decisions openly
- **👥 Community First**: Prioritize community needs
- **🤖 Automation**: Automate repetitive tasks (see Makefile)
- **🤝 Trust**: Build trust through reliability and honesty

## 🔧 Makefile Commands

```bash
make help          # Show all available commands
make setup         # Initial setup
make build         # Build container
make up            # Start application
make down          # Stop application
make logs          # View logs
make test          # Run tests
make clean         # Remove all containers and images
```

## 📁 Project Structure

```
rlteam/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Flask application & routes
│   ├── litemaas_client.py   # LiteMAAS API client
│   └── utils.py             # Utilities & input validation
├── openshift/                     # Kubernetes manifests
├── tests/                   # Test suite
├── Containerfile            # Container build instructions
├── compose.yaml             # Podman Compose configuration
├── Makefile                 # Automation commands
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── .env.template            # Environment template
└── README.md                # This file
```

## 📊 Performance Characteristics

- **Container Size**: ~200MB (UBI Python base)
- **Memory Usage**: ~256MB typical, 512MB limit
- **CPU**: 0.5-1.0 cores
- **Startup Time**: <10 seconds
- **Response Time**: <2 seconds (depends on LiteMAAS)

## 🚧 Future Enhancements

- [ ] Conversation history persistence
- [ ] Multi-language support
- [ ] RAG (Retrieval-Augmented Generation) with knowledge base
- [ ] Prometheus metrics endpoint
- [ ] Rate limiting
- [ ] WebSocket support for streaming responses
- [ ] User authentication

## 📄 License

This demo application is part of the opensourcementor repository.
See the main repository LICENSE file for details.

## 👥 Team

**rlteam** - Red Hat Open Source Hackathon Participant

## 📞 Support

For issues or questions:
1. Check the logs: `make logs`
2. Review the health endpoint: `make health`
3. Consult [GUIDE.md](GUIDE.md) for detailed setup instructions
4. See main repository documentation in `../../docs/`

---

**Built with ❤️ using Podman, Python, and Red Hat Open Source Values**

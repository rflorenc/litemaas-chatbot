# Makefile for Open Source Mentor Bot

# Determine which compose and container command to use
COMPOSE_CMD := $(shell command -v podman-compose 2> /dev/null || command -v docker-compose 2> /dev/null)
CONTAINER_CMD := $(shell command -v podman 2> /dev/null || command -v docker 2> /dev/null)

# Check if .env file exists
ENV_FILE := .env
ENV_CHECK := $(shell test -f $(ENV_FILE) && echo "exists" || echo "missing")

# Load environment variables from .env if it exists
ifneq ($(ENV_CHECK),missing)
    include .env
    export
endif

.PHONY: help setup env venv install build up down restart logs clean shell test lint format health push login dev build-run \
	oc-help oc-check oc-deploy oc-clean oc-rebuild oc-status oc-logs oc-shell oc-url oc-verify oc-build oc-restart oc-scale \
	helm-help helm-check helm-lint helm-template helm-install helm-upgrade helm-uninstall helm-test helm-list helm-status helm-get-values

# Default target
help:
	@echo "Open Source Mentor Bot - Makefile Commands"
	@echo ""
	@echo "Setup & Environment:"
	@echo "  make setup       - Initial setup (create .env, venv)"
	@echo "  make env         - Create .env from template"
	@echo "  make venv        - Create Python virtual environment"
	@echo "  make install     - Install Python dependencies in venv"
	@echo ""
	@echo "Container Operations:"
	@echo "  make build       - Build container image"
	@echo "  make up          - Start container"
	@echo "  make down        - Stop container"
	@echo "  make restart     - Restart container"
	@echo "  make logs        - Show container logs"
	@echo "  make shell       - Open shell in container"
	@echo "  make health      - Check container health"
	@echo ""
	@echo "Development:"
	@echo "  make dev         - Run locally with Python venv"
	@echo "  make build-run   - Clean, build, and run with logs"
	@echo "  make test        - Run tests in container"
	@echo "  make lint        - Run linters"
	@echo "  make format      - Format code with black"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean       - Remove containers, volumes, and images"
	@echo ""
	@echo "OpenShift Operations:"
	@echo "  make oc-help     - Show OpenShift-specific commands"
	@echo "  make oc-check    - Verify OpenShift login and prerequisites"
	@echo "  make oc-deploy   - Deploy to OpenShift (automated script)"
	@echo "  make oc-build    - Rebuild image in OpenShift"
	@echo "  make oc-clean    - Delete all OpenShift resources"
	@echo "  make oc-rebuild  - Clean and redeploy to OpenShift"
	@echo "  make oc-status   - Show status of all resources"
	@echo "  make oc-verify   - Run verification steps"
	@echo "  make oc-logs     - Show application logs"
	@echo "  make oc-url      - Get application URL"
	@echo ""
	@echo "Helm Operations:"
	@echo "  make helm-help       - Show Helm-specific commands"
	@echo "  make helm-check      - Check Helm installation"
	@echo "  make helm-lint       - Lint Helm chart"
	@echo "  make helm-template   - Render Helm templates"
	@echo "  make helm-install    - Install Helm chart"
	@echo "  make helm-upgrade    - Upgrade Helm release"
	@echo "  make helm-uninstall  - Uninstall Helm release"
	@echo ""
	@echo "Using: $(COMPOSE_CMD) and $(CONTAINER_CMD)"

# Setup environment
setup: env venv install
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your LiteMAAS API key"
	@echo "2. Run 'make build' to build the container"
	@echo "3. Run 'make up' to start the application"

# Create .env file from template
env:
	@if [ "$(ENV_CHECK)" = "missing" ]; then \
		echo "Creating .env file from template..."; \
		cp .env.template $(ENV_FILE); \
		echo "✅ .env file created. Please edit with your configuration."; \
	else \
		echo ".env file already exists."; \
	fi

# Create Python virtual environment
venv:
	@if [ ! -d "venv" ]; then \
		echo "Creating Python virtual environment..."; \
		python3 -m venv venv; \
		echo "✅ Virtual environment created."; \
		echo "Activate with: source venv/bin/activate"; \
	else \
		echo "Virtual environment already exists."; \
	fi

# Install dependencies in venv
install:
	@if [ -d "venv" ]; then \
		echo "Installing dependencies in virtual environment..."; \
		. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt; \
		echo "✅ Dependencies installed."; \
	else \
		echo "❌ Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi

# Build container image
build:
	@if [ "$(ENV_CHECK)" = "missing" ]; then \
		echo "❌ .env file not found. Run 'make env' first."; \
		exit 1; \
	fi
	@echo "Building container image..."
	$(COMPOSE_CMD) build
	@echo "✅ Build complete!"

# Start container
up:
	@if [ "$(ENV_CHECK)" = "missing" ]; then \
		echo "❌ .env file not found. Run 'make env' first."; \
		exit 1; \
	fi
	@echo "Starting container..."
	$(COMPOSE_CMD) up -d
	@echo ""
	@echo "✅ Container started!"
	@echo "🚀 Application available at: http://localhost:$(PORT)"
	@echo ""
	@echo "View logs with: make logs"

# Stop container
down:
	@echo "Stopping container..."
	$(COMPOSE_CMD) down
	@echo "✅ Container stopped!"

# Restart container
restart: down up

# Show container logs
logs:
	$(COMPOSE_CMD) logs -f

# Open shell in container
shell:
	@echo "Opening shell in container..."
	$(CONTAINER_CMD) exec -it rlteam-mentor-bot /bin/bash

# Check health endpoint
health:
	@echo "Checking application health..."
	@curl -fsS http://localhost:$(PORT)/health | python3 -m json.tool || echo "❌ Health check failed"

# Clean everything
clean:
	@echo "Removing containers, volumes, and images..."
	$(COMPOSE_CMD) down -v
	$(CONTAINER_CMD) system prune -f
	@echo "✅ Cleanup complete!"

# Run tests in container
test:
	@echo "Running tests..."
	$(CONTAINER_CMD) exec rlteam-mentor-bot pytest tests/ -v

# Run linters
lint:
	@echo "Running linters..."
	$(CONTAINER_CMD) exec rlteam-mentor-bot flake8 app/ tests/

# Format code
format:
	@echo "Formatting code with black..."
	$(CONTAINER_CMD) exec rlteam-mentor-bot black app/ tests/

# Development mode - run locally with venv
dev:
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@if [ "$(ENV_CHECK)" = "missing" ]; then \
		echo "❌ .env file not found. Run 'make env' first."; \
		exit 1; \
	fi
	@echo "Starting development server..."
	@echo "Loading environment from .env..."
	@. venv/bin/activate && set -a && . .env && set +a && python3 run.py

# Build and run with logs
build-run: clean build up logs

#########################################
# OpenShift Operations
#########################################

# OpenShift project name (can be overridden)
OC_PROJECT ?= mentor-bot-rlteam
OC_APP_NAME ?= mentor-bot

# OpenShift-specific help
oc-help:
	@echo "======================================"
	@echo "  OpenShift Operations - Detailed Help"
	@echo "======================================"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - oc CLI installed and in PATH"
	@echo "  - Logged into OpenShift cluster"
	@echo "  - LiteMAAS API key available"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  make oc-check    - Verify you're logged into OpenShift"
	@echo "  make oc-deploy   - Deploy using automated script (uses .env)"
	@echo "  make oc-build    - Rebuild image in OpenShift BuildConfig"
	@echo "  make oc-rebuild  - Clean everything and redeploy"
	@echo ""
	@echo "Customization:"
	@echo "  BUILD_STRATEGY=1 make oc-deploy  - Override build strategy"
	@echo "    1 = BuildConfig (in cluster)"
	@echo "    2 = Internal Registry (push local)"
	@echo "    3 = Skip build (use existing)"
	@echo ""
	@echo "Monitoring Commands:"
	@echo "  make oc-status   - Show status of all resources"
	@echo "  make oc-logs     - Follow application logs"
	@echo "  make oc-shell    - Open shell in running pod"
	@echo "  make oc-url      - Get application route URL"
	@echo "  make oc-verify   - Run complete verification checks"
	@echo ""
	@echo "Management Commands:"
	@echo "  make oc-restart  - Restart the deployment"
	@echo "  make oc-scale N=3 - Scale to N replicas"
	@echo "  make oc-clean    - Delete all OpenShift resources"
	@echo ""
	@echo "Manual Verification Steps:"
	@echo "  1. make oc-status      # Check resource status"
	@echo "  2. make oc-logs        # Check application logs"
	@echo "  3. make oc-url         # Get application URL"
	@echo "  4. make oc-verify      # Run all checks"
	@echo ""
	@echo "Current project: $(OC_PROJECT)"
	@echo ""

# Check OpenShift login and prerequisites
oc-check:
	@echo "🔍 Checking OpenShift prerequisites..."
	@command -v oc >/dev/null 2>&1 || { echo "❌ oc CLI not found. Please install OpenShift CLI."; exit 1; }
	@echo "✅ oc CLI found: $$(oc version --client -o json | grep -o '"gitVersion":"[^"]*' | cut -d'"' -f4)"
	@oc whoami >/dev/null 2>&1 || { echo "❌ Not logged into OpenShift. Run: oc login"; exit 1; }
	@echo "✅ Logged in as: $$(oc whoami)"
	@echo "✅ Server: $$(oc whoami --show-server)"
	@echo "✅ Current project: $$(oc project -q 2>/dev/null || echo 'None')"
	@if [ ! -f "Dockerfile" ] && [ -f "Containerfile" ]; then \
		echo "⚠️  Creating Dockerfile symlink for OpenShift..."; \
		ln -sf Containerfile Dockerfile; \
	fi
	@echo "✅ All prerequisites met!"

# Deploy to OpenShift using automated script
oc-deploy: oc-check
	@echo "🚀 Deploying to OpenShift..."
	@if [ "$(ENV_CHECK)" = "missing" ]; then \
		echo "❌ .env file not found. Run 'make env' first."; \
		exit 1; \
	fi
	@if [ -z "$(LITEMAAS_API_KEY)" ]; then \
		echo "❌ LITEMAAS_API_KEY not set in .env file."; \
		exit 1; \
	fi
	@chmod +x openshift-deploy.sh
	@echo "Using configuration from .env file..."
	@OC_PROJECT="$(OC_PROJECT)" \
	 LITEMAAS_API_KEY="$(LITEMAAS_API_KEY)" \
	 BUILD_STRATEGY="$${BUILD_STRATEGY:-1}" \
	 ./openshift-deploy.sh

# Rebuild image in OpenShift
oc-build: oc-check
	@echo "🔨 Rebuilding image in OpenShift..."
	@if [ ! -f "Dockerfile" ] && [ -f "Containerfile" ]; then \
		ln -sf Containerfile Dockerfile; \
	fi
	@if oc get bc/$(OC_APP_NAME) >/dev/null 2>&1; then \
		echo "Starting build from local source..."; \
		oc start-build $(OC_APP_NAME) --from-dir=. --follow; \
		echo ""; \
		echo "Updating deployment to use new image..."; \
		PROJECT=$$(oc project -q); \
		oc set image deployment/$(OC_APP_NAME) $(OC_APP_NAME)=image-registry.openshift-image-registry.svc:5000/$$PROJECT/$(OC_APP_NAME):latest; \
	else \
		echo "❌ BuildConfig not found. Run 'make oc-deploy' first."; \
		exit 1; \
	fi
	@echo "✅ Image rebuilt and deployment updated!"

# Show status of all OpenShift resources
oc-status: oc-check
	@echo "📊 OpenShift Resource Status"
	@echo "======================================"
	@echo ""
	@echo "Project:"
	@oc project
	@echo ""
	@echo "All Resources:"
	@oc get all
	@echo ""
	@echo "ConfigMaps:"
	@oc get cm -l app=$(OC_APP_NAME)
	@echo ""
	@echo "Secrets:"
	@oc get secret -l app=$(OC_APP_NAME)
	@echo ""
	@echo "Routes:"
	@oc get route -l app=$(OC_APP_NAME)
	@echo ""
	@echo "Recent Events:"
	@oc get events --sort-by='.lastTimestamp' | head -10

# Show application logs
oc-logs: oc-check
	@echo "📋 Following application logs..."
	@echo "Press Ctrl+C to stop"
	@echo ""
	@oc logs -f deployment/$(OC_APP_NAME)

# Open shell in running pod
oc-shell: oc-check
	@echo "🐚 Opening shell in pod..."
	@POD=$$(oc get pods -l app=$(OC_APP_NAME) -o name | head -1); \
	if [ -z "$$POD" ]; then \
		echo "❌ No running pods found"; \
		exit 1; \
	fi; \
	echo "Connecting to $$POD..."; \
	oc exec -it $$POD -- /bin/bash

# Get application URL
oc-url: oc-check
	@echo "🌐 Application URL:"
	@ROUTE_URL=$$(oc get route $(OC_APP_NAME)-route -o jsonpath='{.spec.host}' 2>/dev/null); \
	if [ -z "$$ROUTE_URL" ]; then \
		echo "❌ Route not found"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "  https://$$ROUTE_URL"; \
	echo ""; \
	echo "Health Check:"; \
	echo "  curl https://$$ROUTE_URL/health"; \
	echo ""; \
	echo "Chat API:"; \
	echo "  curl -X POST https://$$ROUTE_URL/api/chat \\"; \
	echo "    -H 'Content-Type: application/json' \\"; \
	echo "    -d '{\"message\": \"Hello!\"}'"; \
	echo ""

# Restart the deployment
oc-restart: oc-check
	@echo "♻️  Restarting deployment..."
	@oc rollout restart deployment/$(OC_APP_NAME)
	@echo "⏳ Waiting for rollout to complete..."
	@oc rollout status deployment/$(OC_APP_NAME)
	@echo "✅ Deployment restarted successfully!"

# Scale the deployment
oc-scale: oc-check
	@if [ -z "$(N)" ]; then \
		echo "❌ Please specify number of replicas: make oc-scale N=3"; \
		exit 1; \
	fi
	@echo "⚖️  Scaling to $(N) replicas..."
	@oc scale deployment/$(OC_APP_NAME) --replicas=$(N)
	@echo "✅ Scaled to $(N) replicas"
	@oc get pods -l app=$(OC_APP_NAME)

# Run complete verification
oc-verify: oc-check
	@echo "✅ Running OpenShift Deployment Verification"
	@echo "======================================"
	@echo ""
	@echo "1️⃣  Checking Project..."
	@oc project
	@echo ""
	@echo "2️⃣  Checking Pods..."
	@POD_STATUS=$$(oc get pods -l app=$(OC_APP_NAME) -o jsonpath='{.items[0].status.phase}' 2>/dev/null); \
	if [ "$$POD_STATUS" = "Running" ]; then \
		echo "✅ Pod is running"; \
		oc get pods -l app=$(OC_APP_NAME); \
	else \
		echo "❌ Pod status: $$POD_STATUS"; \
		oc get pods -l app=$(OC_APP_NAME); \
		exit 1; \
	fi
	@echo ""
	@echo "3️⃣  Checking Service..."
	@if oc get svc $(OC_APP_NAME)-service >/dev/null 2>&1; then \
		echo "✅ Service exists"; \
		oc get svc $(OC_APP_NAME)-service; \
	else \
		echo "❌ Service not found"; \
		exit 1; \
	fi
	@echo ""
	@echo "4️⃣  Checking Route..."
	@ROUTE_URL=$$(oc get route $(OC_APP_NAME)-route -o jsonpath='{.spec.host}' 2>/dev/null); \
	if [ -n "$$ROUTE_URL" ]; then \
		echo "✅ Route exists: https://$$ROUTE_URL"; \
	else \
		echo "❌ Route not found"; \
		exit 1; \
	fi
	@echo ""
	@echo "5️⃣  Checking Health Endpoint..."
	@ROUTE_URL=$$(oc get route $(OC_APP_NAME)-route -o jsonpath='{.spec.host}'); \
	if curl -fsS --max-time 10 "https://$$ROUTE_URL/health" >/dev/null 2>&1; then \
		echo "✅ Health endpoint responding"; \
		curl -s "https://$$ROUTE_URL/health" | python3 -m json.tool; \
	else \
		echo "❌ Health endpoint not responding"; \
		echo "Checking pod logs..."; \
		oc logs -l app=$(OC_APP_NAME) --tail=20; \
		exit 1; \
	fi
	@echo ""
	@echo "6️⃣  Checking ConfigMap..."
	@if oc get cm $(OC_APP_NAME)-config >/dev/null 2>&1; then \
		echo "✅ ConfigMap exists"; \
	else \
		echo "❌ ConfigMap not found"; \
		exit 1; \
	fi
	@echo ""
	@echo "7️⃣  Checking Secrets..."
	@if oc get secret $(OC_APP_NAME)-secrets >/dev/null 2>&1; then \
		echo "✅ Secrets exist"; \
	else \
		echo "❌ Secrets not found"; \
		exit 1; \
	fi
	@echo ""
	@echo "8️⃣  Checking ServiceAccount..."
	@if oc get sa $(OC_APP_NAME)-sa >/dev/null 2>&1; then \
		echo "✅ ServiceAccount exists"; \
	else \
		echo "⚠️  ServiceAccount not found (optional)"; \
	fi
	@echo ""
	@echo "9️⃣  Testing Chat API..."
	@ROUTE_URL=$$(oc get route $(OC_APP_NAME)-route -o jsonpath='{.spec.host}'); \
	RESPONSE=$$(curl -fsS --max-time 30 -X POST "https://$$ROUTE_URL/api/chat" \
		-H 'Content-Type: application/json' \
		-d '{"message": "Hello"}' 2>/dev/null); \
	if [ $$? -eq 0 ]; then \
		echo "✅ Chat API responding"; \
		echo "$$RESPONSE" | python3 -m json.tool | head -5; \
	else \
		echo "❌ Chat API not responding"; \
		exit 1; \
	fi
	@echo ""
	@echo "🔟  Checking Resource Usage..."
	@if oc adm top pods -l app=$(OC_APP_NAME) >/dev/null 2>&1; then \
		oc adm top pods -l app=$(OC_APP_NAME); \
	else \
		echo "⚠️  Metrics not available (metrics server may not be running)"; \
	fi
	@echo ""
	@echo "======================================"
	@echo "✅ All verification checks passed!"
	@echo "======================================"
	@echo ""
	@echo "Application URL: https://$$(oc get route $(OC_APP_NAME)-route -o jsonpath='{.spec.host}')"
	@echo ""

# Clean all OpenShift resources
oc-clean: oc-check
	@echo "🗑️  Cleaning OpenShift resources..."
	@echo "⚠️  This will delete all resources in the current project"
	@echo "Project: $$(oc project -q)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Deleting resources..."; \
		oc delete all,cm,secret,route,sa -l app=$(OC_APP_NAME) 2>/dev/null || true; \
		oc delete secret mentor-bot-secrets 2>/dev/null || true; \
		oc delete bc/$(OC_APP_NAME) 2>/dev/null || true; \
		oc delete is/$(OC_APP_NAME) 2>/dev/null || true; \
		echo "✅ Resources deleted"; \
	else \
		echo "❌ Cancelled"; \
	fi

# Clean and rebuild everything
oc-rebuild: oc-clean oc-deploy
	@echo "✅ Rebuild complete!"

#########################################
# Helm Operations
#########################################

# Helm configuration
HELM_CHART_PATH := ./helm/mentor-bot
HELM_RELEASE_NAME ?= mentor-bot
HELM_NAMESPACE ?= mentor-bot-rlteam
HELM_VALUES_FILE := $(HELM_CHART_PATH)/values.yaml
HELM_OPENSHIFT_VALUES := $(HELM_CHART_PATH)/values-openshift.yaml

# Helm-specific help
helm-help:
	@echo "======================================"
	@echo "  Helm Operations - Detailed Help"
	@echo "======================================"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - helm CLI installed (v3.0+)"
	@echo "  - oc or kubectl configured"
	@echo "  - LiteMAAS API key available"
	@echo ""
	@echo "Chart Management:"
	@echo "  make helm-check      - Verify Helm installation"
	@echo "  make helm-lint       - Validate chart syntax and structure"
	@echo "  make helm-template   - Render templates without installing"
	@echo "  make helm-package    - Package chart into archive"
	@echo ""
	@echo "Deployment:"
	@echo "  make helm-install    - Install chart (OpenShift optimized)"
	@echo "  make helm-upgrade    - Upgrade existing release"
	@echo "  make helm-uninstall  - Remove Helm release"
	@echo ""
	@echo "Customization:"
	@echo "  HELM_RELEASE_NAME=my-bot make helm-install"
	@echo "  HELM_NAMESPACE=production make helm-install"
	@echo "  API_KEY=sk-xxx make helm-install"
	@echo ""
	@echo "Monitoring:"
	@echo "  make helm-list       - List all Helm releases"
	@echo "  make helm-status     - Show release status"
	@echo "  make helm-get-values - Show current values"
	@echo "  make helm-history    - Show release history"
	@echo "  make helm-test       - Run chart tests"
	@echo ""
	@echo "Development:"
	@echo "  make helm-debug      - Install with debug output"
	@echo "  make helm-diff       - Show diff before upgrade"
	@echo "  make helm-rollback   - Rollback to previous version"
	@echo ""
	@echo "Current settings:"
	@echo "  Chart:     $(HELM_CHART_PATH)"
	@echo "  Release:   $(HELM_RELEASE_NAME)"
	@echo "  Namespace: $(HELM_NAMESPACE)"
	@echo ""

# Check Helm installation
helm-check:
	@echo "🔍 Checking Helm installation..."
	@command -v helm >/dev/null 2>&1 || { echo "❌ helm CLI not found. Please install Helm."; exit 1; }
	@echo "✅ Helm version: $$(helm version --short)"
	@command -v oc >/dev/null 2>&1 && echo "✅ oc CLI found: $$(oc version --client --short 2>/dev/null || echo 'version unknown')" || true
	@command -v kubectl >/dev/null 2>&1 && echo "✅ kubectl found: $$(kubectl version --client --short 2>/dev/null || echo 'version unknown')" || true
	@echo "✅ Chart location: $(HELM_CHART_PATH)"
	@test -f "$(HELM_CHART_PATH)/Chart.yaml" || { echo "❌ Chart.yaml not found"; exit 1; }
	@echo "✅ Chart.yaml found"
	@echo "✅ All prerequisites met!"

# Lint Helm chart
helm-lint: helm-check
	@echo "🔍 Linting Helm chart..."
	@helm lint $(HELM_CHART_PATH)
	@echo "✅ Chart validation passed!"

# Render Helm templates
helm-template: helm-check
	@echo "📄 Rendering Helm templates..."
	@helm template $(HELM_RELEASE_NAME) $(HELM_CHART_PATH) \
		-f $(HELM_OPENSHIFT_VALUES) \
		--namespace $(HELM_NAMESPACE)

# Render templates with custom API key
helm-template-with-key: helm-check
	@if [ -z "$(API_KEY)" ]; then \
		echo "❌ API_KEY not set. Usage: API_KEY=your-key make helm-template-with-key"; \
		exit 1; \
	fi
	@echo "📄 Rendering Helm templates with custom API key..."
	@helm template $(HELM_RELEASE_NAME) $(HELM_CHART_PATH) \
		-f $(HELM_OPENSHIFT_VALUES) \
		--set secrets.data.LITEMAAS_API_KEY="$(API_KEY)" \
		--namespace $(HELM_NAMESPACE)

# Package Helm chart
helm-package: helm-check helm-lint
	@echo "📦 Packaging Helm chart..."
	@helm package $(HELM_CHART_PATH) -d ./dist
	@echo "✅ Chart packaged successfully!"

# Install Helm chart (OpenShift)
helm-install: helm-check helm-lint
	@echo "🚀 Installing Helm chart to OpenShift..."
	@if [ -z "$(API_KEY)" ]; then \
		if [ -z "$(LITEMAAS_API_KEY)" ]; then \
			echo "❌ API key not set. Please set API_KEY or LITEMAAS_API_KEY"; \
			echo "Usage: API_KEY=your-key make helm-install"; \
			exit 1; \
		else \
			API_KEY="$(LITEMAAS_API_KEY)"; \
		fi; \
	fi; \
	if ! oc get project $(HELM_NAMESPACE) >/dev/null 2>&1; then \
		echo "Creating namespace $(HELM_NAMESPACE)..."; \
		oc new-project $(HELM_NAMESPACE); \
	fi; \
	helm install $(HELM_RELEASE_NAME) $(HELM_CHART_PATH) \
		-f $(HELM_OPENSHIFT_VALUES) \
		--set secrets.data.LITEMAAS_API_KEY="$$API_KEY" \
		--namespace $(HELM_NAMESPACE) \
		--create-namespace
	@echo "✅ Helm chart installed successfully!"

# Upgrade Helm release
helm-upgrade: helm-check helm-lint
	@echo "⬆️  Upgrading Helm release..."
	@if [ -n "$(API_KEY)" ]; then \
		helm upgrade $(HELM_RELEASE_NAME) $(HELM_CHART_PATH) \
			-f $(HELM_OPENSHIFT_VALUES) \
			--set secrets.data.LITEMAAS_API_KEY="$(API_KEY)" \
			--namespace $(HELM_NAMESPACE); \
	else \
		helm upgrade $(HELM_RELEASE_NAME) $(HELM_CHART_PATH) \
			-f $(HELM_OPENSHIFT_VALUES) \
			--namespace $(HELM_NAMESPACE); \
	fi
	@echo "✅ Helm release upgraded successfully!"

# Uninstall Helm release
helm-uninstall: helm-check
	@echo "🗑️  Uninstalling Helm release..."
	@helm uninstall $(HELM_RELEASE_NAME) --namespace $(HELM_NAMESPACE)
	@echo "✅ Helm release uninstalled!"

# List Helm releases
helm-list: helm-check
	@echo "📋 Helm releases:"
	@helm list --namespace $(HELM_NAMESPACE)

# Show Helm release status
helm-status: helm-check
	@echo "📊 Release status:"
	@helm status $(HELM_RELEASE_NAME) --namespace $(HELM_NAMESPACE)

# Get current values
helm-get-values: helm-check
	@echo "⚙️  Current Helm values:"
	@helm get values $(HELM_RELEASE_NAME) --namespace $(HELM_NAMESPACE)

# Show release history
helm-history: helm-check
	@echo "📜 Release history:"
	@helm history $(HELM_RELEASE_NAME) --namespace $(HELM_NAMESPACE)

# Run Helm tests
helm-test: helm-check
	@echo "🧪 Running Helm tests..."
	@helm test $(HELM_RELEASE_NAME) --namespace $(HELM_NAMESPACE)

# Install with debug
helm-debug: helm-check helm-lint
	@echo "🐛 Installing with debug output..."
	@helm install $(HELM_RELEASE_NAME) $(HELM_CHART_PATH) \
		-f $(HELM_OPENSHIFT_VALUES) \
		--namespace $(HELM_NAMESPACE) \
		--debug \
		--dry-run

# Show diff before upgrade
helm-diff: helm-check
	@echo "🔍 Showing diff..."
	@command -v helm-diff >/dev/null 2>&1 || { echo "❌ helm-diff plugin not installed. Run: helm plugin install https://github.com/databus23/helm-diff"; exit 1; }
	@helm diff upgrade $(HELM_RELEASE_NAME) $(HELM_CHART_PATH) \
		-f $(HELM_OPENSHIFT_VALUES) \
		--namespace $(HELM_NAMESPACE)

# Rollback to previous version
helm-rollback: helm-check
	@echo "⏪ Rolling back to previous version..."
	@helm rollback $(HELM_RELEASE_NAME) --namespace $(HELM_NAMESPACE)
	@echo "✅ Rollback complete!"

# Get application URL (OpenShift)
helm-url: helm-check
	@echo "🌐 Application URL:"
	@ROUTE_URL=$$(oc get route $(HELM_RELEASE_NAME)-route -n $(HELM_NAMESPACE) -o jsonpath='{.spec.host}' 2>/dev/null); \
	if [ -z "$$ROUTE_URL" ]; then \
		echo "❌ Route not found"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "  https://$$ROUTE_URL"; \
	echo ""; \
	echo "Health Check:"; \
	echo "  curl https://$$ROUTE_URL/health"

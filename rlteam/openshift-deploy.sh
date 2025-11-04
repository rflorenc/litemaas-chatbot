#!/bin/bash
# OpenShift Deployment Automation Script for Open Source Mentor Bot
# This script automates the deployment of the application to OpenShift
#
# Usage:
#   Interactive: ./openshift-deploy.sh
#   Non-interactive: OC_PROJECT=my-project LITEMAAS_API_KEY=sk-xxx BUILD_STRATEGY=1 ./openshift-deploy.sh
#   Via Make: make oc-deploy (uses .env file)
#
# Environment Variables:
#   OC_PROJECT        - OpenShift project name (default: mentor-bot-rlteam)
#   LITEMAAS_API_KEY  - LiteMAAS API key (required)
#   BUILD_STRATEGY    - 1=BuildConfig, 2=Internal Registry, 3=Skip (default: 1)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if oc is installed
    if ! command -v oc &> /dev/null; then
        log_error "oc CLI not found. Please install OpenShift CLI."
        exit 1
    fi

    # Check if logged into OpenShift
    if ! oc whoami &> /dev/null; then
        log_error "Not logged into OpenShift. Please run: oc login"
        exit 1
    fi

    # Check if podman is installed
    if ! command -v podman &> /dev/null; then
        log_error "podman not found. Please install Podman."
        exit 1
    fi

    log_success "All prerequisites met!"
}

get_user_input() {
    log_info "Gathering deployment information..."

    # Project name - check if already provided via environment
    if [ -z "$OC_PROJECT" ]; then
        read -p "Enter OpenShift project name [mentor-bot-rlteam]: " PROJECT_NAME
        PROJECT_NAME=${PROJECT_NAME:-mentor-bot-rlteam}
    else
        PROJECT_NAME="$OC_PROJECT"
        log_info "Using project name from environment: $PROJECT_NAME"
    fi

    # LiteMAAS API Key - check if already provided via environment
    if [ -z "$LITEMAAS_API_KEY" ]; then
        read -sp "Enter LiteMAAS API key: " LITEMAAS_API_KEY
        echo

        if [ -z "$LITEMAAS_API_KEY" ]; then
            log_error "LiteMAAS API key is required!"
            exit 1
        fi
    else
        log_info "Using LiteMAAS API key from environment"
    fi

    # Image build strategy - check if already provided via environment
    if [ -z "$BUILD_STRATEGY" ]; then
        echo
        log_info "Choose image build strategy:"
        echo "1) OpenShift BuildConfig (recommended - builds in cluster)"
        echo "2) OpenShift Internal Registry (push from local)"
        echo "3) Skip image build (use existing image)"
        read -p "Enter choice [1]: " BUILD_STRATEGY
        BUILD_STRATEGY=${BUILD_STRATEGY:-1}
    else
        log_info "Using build strategy from environment: $BUILD_STRATEGY"
    fi
}

create_project() {
    log_info "Creating OpenShift project: $PROJECT_NAME"

    if oc get project "$PROJECT_NAME" &> /dev/null; then
        log_warning "Project $PROJECT_NAME already exists. Using existing project."
        oc project "$PROJECT_NAME"
    else
        oc new-project "$PROJECT_NAME"
        log_success "Project $PROJECT_NAME created!"
    fi
}

build_image_buildconfig() {
    log_info "Setting up BuildConfig..."

    # Use OpenShift-specific Containerfile if it exists
    DOCKERFILE_PATH="Containerfile"
    if [ -f "openshift/Containerfile.openshift" ]; then
        log_info "Using OpenShift-compatible Containerfile..."
        cp openshift/Containerfile.openshift Dockerfile
    elif [ ! -f Dockerfile ] && [ -f Containerfile ]; then
        log_info "Creating Dockerfile symlink for OpenShift..."
        ln -sf Containerfile Dockerfile
    fi

    # Check if BuildConfig exists
    if oc get bc/mentor-bot &> /dev/null; then
        log_warning "BuildConfig already exists. Rebuilding..."
        oc start-build mentor-bot --from-dir=. --follow
    else
        # Create new BuildConfig
        oc new-build --name=mentor-bot --binary --strategy=docker
        log_success "BuildConfig created!"

        # Start the build
        log_info "Starting build from local source..."
        oc start-build mentor-bot --from-dir=. --follow
    fi

    log_success "Image built successfully!"

    # Update deployment to use ImageStream with full path
    # OpenShift needs the full registry path to pull from ImageStream
    IMAGE_REF="image-registry.openshift-image-registry.svc:5000/$PROJECT_NAME/mentor-bot:latest"
}

build_image_registry() {
    log_info "Building and pushing to OpenShift internal registry..."

    # Get registry URL
    REGISTRY=$(oc get route default-route -n openshift-image-registry \
        --template='{{ .spec.host }}' 2>/dev/null || echo "")

    if [ -z "$REGISTRY" ]; then
        REGISTRY="image-registry.openshift-image-registry.svc:5000"
        log_warning "Using internal registry: $REGISTRY"
    fi

    # Build locally
    log_info "Building image locally..."
    podman build -t mentor-bot:latest .

    # Tag for registry
    IMAGE_REF="$REGISTRY/$PROJECT_NAME/mentor-bot:latest"
    podman tag mentor-bot:latest "$IMAGE_REF"

    # Login to registry
    log_info "Logging into OpenShift registry..."
    podman login -u "$(oc whoami)" -p "$(oc whoami -t)" "$REGISTRY" --tls-verify=false

    # Push image
    log_info "Pushing image to registry..."
    podman push "$IMAGE_REF" --tls-verify=false

    log_success "Image pushed successfully!"
}

create_secrets() {
    log_info "Creating secrets..."

    # Delete existing secret if it exists
    if oc get secret mentor-bot-secrets &> /dev/null; then
        log_warning "Secret already exists. Updating..."
        oc delete secret mentor-bot-secrets
    fi

    # Create secret
    oc create secret generic mentor-bot-secrets \
        --from-literal=LITEMAAS_API_KEY="$LITEMAAS_API_KEY"

    log_success "Secrets created!"
}

deploy_application() {
    log_info "Deploying application..."

    # Apply ServiceAccount first
    oc apply -f openshift/serviceaccount.yaml
    log_success "ServiceAccount applied"

    # Apply ConfigMap
    oc apply -f openshift/configmap.yaml
    log_success "ConfigMap applied"

    # Use OpenShift deployment
    DEPLOYMENT_FILE="openshift/deployment.yaml"
    log_info "Using OpenShift deployment..."

    # Update deployment image if needed
    if [ -n "$IMAGE_REF" ]; then
        log_info "Updating deployment with image: $IMAGE_REF"
        # Create temporary deployment file with updated image
        sed "s|image: mentor-bot:latest|image: $IMAGE_REF|g" "$DEPLOYMENT_FILE" > /tmp/deployment.yaml
        oc apply -f /tmp/deployment.yaml
        rm /tmp/deployment.yaml
    else
        oc apply -f "$DEPLOYMENT_FILE"
    fi
    log_success "Deployment applied"

    # Apply Service
    oc apply -f openshift/service.yaml
    log_success "Service applied"

    # Apply Route
    oc apply -f openshift/route.yaml
    log_success "Route applied"
}

wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."

    oc rollout status deployment/mentor-bot --timeout=5m

    log_success "Deployment is ready!"
}

display_access_info() {
    echo
    log_success "🎉 Deployment completed successfully!"
    echo

    # Get route URL
    ROUTE_URL=$(oc get route mentor-bot-route -o jsonpath='{.spec.host}')

    echo "======================================"
    echo "  Application Access Information"
    echo "======================================"
    echo
    echo "Project:      $PROJECT_NAME"
    echo "Application:  https://$ROUTE_URL"
    echo "Health Check: https://$ROUTE_URL/health"
    echo
    echo "Useful Commands:"
    echo "  View logs:     oc logs -f deployment/mentor-bot"
    echo "  View pods:     oc get pods"
    echo "  View all:      oc get all"
    echo "  Delete app:    oc delete -f openshift/"
    echo

    # Test health endpoint
    log_info "Testing health endpoint..."
    if curl -fsS "https://$ROUTE_URL/health" &> /dev/null; then
        log_success "Application is healthy!"
    else
        log_warning "Health check failed. Check logs: oc logs deployment/mentor-bot"
    fi
}

# Main execution
main() {
    echo "======================================"
    echo "  OpenShift Deployment Script"
    echo "  Open Source Mentor Bot"
    echo "======================================"
    echo

    # Check prerequisites
    check_prerequisites

    # Get user input
    get_user_input

    # Create project
    create_project

    # Build and push image
    case $BUILD_STRATEGY in
        1)
            build_image_buildconfig
            ;;
        2)
            build_image_registry
            ;;
        3)
            log_warning "Skipping image build. Using existing image."
            IMAGE_REF=""
            ;;
        *)
            log_error "Invalid choice!"
            exit 1
            ;;
    esac

    # Create secrets
    create_secrets

    # Deploy application
    deploy_application

    # Wait for deployment
    wait_for_deployment

    # Display access information
    display_access_info
}

# Run main function
main

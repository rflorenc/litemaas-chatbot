#!/bin/bash
# Quick Start Script for Open Source Mentor Bot
# This script automates the initial setup process

set -e

echo "🤖 Open Source Mentor Bot - Quick Start"
echo "========================================"
echo ""

# Check for required commands
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

# Detect which container runtime to use
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    echo "✅ Using Podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker-compose"
    echo "✅ Using Docker"
else
    echo "❌ Neither Podman nor Docker found. Please install one of them."
    exit 1
fi

echo ""

# Check for compose command
if ! command -v $COMPOSE_CMD &> /dev/null; then
    echo "❌ $COMPOSE_CMD is not installed."
    echo "   Install it with: pip install podman-compose"
    exit 1
fi

echo "✅ $COMPOSE_CMD is available"
echo ""

# Step 1: Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your LiteMAAS API key"
    echo "   Run: vim .env (or nano .env)"
    echo ""
    read -p "Press Enter once you've updated the .env file..."
else
    echo "✅ .env file already exists"
fi

echo ""

# Step 2: Create Python virtual environment (optional for local dev)
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Virtual environment created and dependencies installed"
else
    echo "✅ Virtual environment already exists"
fi

echo ""

# Step 3: Build container image
echo "🏗️  Building container image..."
$COMPOSE_CMD build

echo ""
echo "✅ Container image built successfully"
echo ""

# Step 4: Start the application
echo "🚀 Starting the application..."
$COMPOSE_CMD up -d

echo ""
echo "✅ Application started!"
echo ""

# Wait a few seconds for the app to start
echo "⏳ Waiting for application to be ready..."
sleep 5

# Step 5: Check health
echo ""
echo "🏥 Checking application health..."
if curl -fsS http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
else
    echo "⚠️  Health check failed. Check logs with: $COMPOSE_CMD logs"
fi

echo ""
echo "=========================================="
echo "🎉 Setup Complete!"
echo "=========================================="
echo ""
echo "Your Open Source Mentor Bot is running at:"
echo "  🌐 http://localhost:8080"
echo ""
echo "Useful commands:"
echo "  📋 View logs:       $COMPOSE_CMD logs -f"
echo "  🛑 Stop app:        $COMPOSE_CMD down"
echo "  🔄 Restart:         $COMPOSE_CMD restart"
echo "  🏥 Check health:    curl http://localhost:8080/health"
echo "  🧪 Run tests:       ./run_tests.sh"
echo ""
echo "For more information, see README.md and GUIDE.md"
echo ""

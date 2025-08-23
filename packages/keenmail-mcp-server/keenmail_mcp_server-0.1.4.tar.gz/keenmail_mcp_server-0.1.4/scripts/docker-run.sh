#!/bin/bash
set -euo pipefail

# KeenMail MCP Server - Docker Run Script
# Usage: ./scripts/docker-run.sh [--prod] [--build] [--logs]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Default values
COMPOSE_FILE="docker-compose.yml"
BUILD=false
LOGS=false
DETACH=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prod)
            COMPOSE_FILE="docker-compose.prod.yml"
            shift
            ;;
        --dev)
            COMPOSE_FILE="docker-compose.yml"
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --logs|-l)
            LOGS=true
            DETACH=false
            shift
            ;;
        --foreground|-f)
            DETACH=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --prod                 Use production compose file"
            echo "  --dev                  Use development compose file (default)"
            echo "  --build                Build image before running"
            echo "  --logs, -l             Show logs (implies --foreground)"
            echo "  --foreground, -f       Run in foreground"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     # Run in development mode"
            echo "  $0 --prod              # Run in production mode"
            echo "  $0 --build --logs      # Build and show logs"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if .env file exists
if [[ ! -f .env ]]; then
    if [[ -f .env.docker ]]; then
        echo "📝 Copying .env.docker to .env..."
        cp .env.docker .env
        echo ""
        echo "⚠️  Please edit .env file with your actual API credentials:"
        echo "   KEENMAIL_API_KEY=your_actual_key"
        echo "   KEENMAIL_SECRET=your_actual_secret"
        echo ""
        read -p "Press Enter when you've updated the .env file..."
    else
        echo "❌ No .env file found!"
        echo "Please create a .env file with your KeenMail credentials:"
        echo ""
        echo "KEENMAIL_API_KEY=your_api_key"
        echo "KEENMAIL_SECRET=your_secret"
        echo ""
        exit 1
    fi
fi

# Validate environment variables
source .env
if [[ -z "${KEENMAIL_API_KEY:-}" ]] || [[ "${KEENMAIL_API_KEY}" == "your_api_key_here" ]]; then
    echo "❌ Please set KEENMAIL_API_KEY in .env file"
    exit 1
fi
if [[ -z "${KEENMAIL_SECRET:-}" ]] || [[ "${KEENMAIL_SECRET}" == "your_secret_key_here" ]]; then
    echo "❌ Please set KEENMAIL_SECRET in .env file"
    exit 1
fi

echo "🐳 Starting KeenMail MCP Server..."
echo "📋 Compose file: $COMPOSE_FILE"
echo ""

# Build if requested
if [[ "$BUILD" == "true" ]]; then
    echo "🔨 Building image..."
    docker-compose -f "$COMPOSE_FILE" build
    echo ""
fi

# Run the service
COMPOSE_ARGS=("up")
if [[ "$DETACH" == "true" ]]; then
    COMPOSE_ARGS+=("-d")
fi

docker-compose -f "$COMPOSE_FILE" "${COMPOSE_ARGS[@]}"

if [[ "$DETACH" == "true" && "$LOGS" == "false" ]]; then
    echo "✅ KeenMail MCP Server started successfully!"
    echo ""
    echo "📊 To check status:"
    echo "   docker-compose -f $COMPOSE_FILE ps"
    echo ""
    echo "📋 To view logs:"
    echo "   docker-compose -f $COMPOSE_FILE logs -f"
    echo ""
    echo "🛑 To stop:"
    echo "   docker-compose -f $COMPOSE_FILE down"
fi

if [[ "$LOGS" == "true" ]]; then
    echo "📋 Following logs... (Ctrl+C to stop)"
    docker-compose -f "$COMPOSE_FILE" logs -f
fi
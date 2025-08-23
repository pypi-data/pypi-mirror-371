#!/bin/bash
set -euo pipefail

# KeenMail MCP Server - Docker Build Script
# Usage: ./scripts/docker-build.sh [--push] [--platform linux/amd64,linux/arm64]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Default values
PUSH=false
PLATFORM="linux/amd64"
IMAGE_NAME="keenmail-mcp-server"
TAG="latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --push                  Push image to registry after build"
            echo "  --platform PLATFORMS    Target platforms (default: linux/amd64)"
            echo "  --tag TAG              Image tag (default: latest)"
            echo "  --image NAME           Image name (default: keenmail-mcp-server)"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     # Build for linux/amd64"
            echo "  $0 --push --tag v0.1.0"
            echo "  $0 --platform linux/amd64,linux/arm64 --push"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get version from pyproject.toml if tag is 'latest'
if [[ "$TAG" == "latest" ]]; then
    VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    if [[ -n "$VERSION" ]]; then
        TAG="v$VERSION"
    fi
fi

echo "🐳 Building Docker image: $IMAGE_NAME:$TAG"
echo "📦 Platform(s): $PLATFORM"
echo "🚀 Push: $PUSH"
echo ""

# Build arguments
BUILD_ARGS=(
    "build"
    "--platform" "$PLATFORM"
    "--tag" "$IMAGE_NAME:$TAG"
    "--tag" "$IMAGE_NAME:latest"
    "--file" "Dockerfile"
    "--label" "org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    "--label" "org.opencontainers.image.version=$TAG"
    "--label" "org.opencontainers.image.revision=$(git rev-parse HEAD)"
    "."
)

if [[ "$PUSH" == "true" ]]; then
    BUILD_ARGS+=("--push")
fi

# Check if buildx is available for multi-platform builds
if [[ "$PLATFORM" == *","* ]] || [[ "$PUSH" == "true" ]]; then
    echo "🔧 Using docker buildx for multi-platform build..."
    docker buildx "${BUILD_ARGS[@]}"
else
    echo "🔧 Using standard docker build..."
    # Remove --platform for single platform standard build
    BUILD_ARGS=("${BUILD_ARGS[@]/--platform/}")
    BUILD_ARGS=("${BUILD_ARGS[@]/$PLATFORM/}")
    docker "${BUILD_ARGS[@]}"
fi

echo ""
echo "✅ Build completed successfully!"
echo "📋 Image: $IMAGE_NAME:$TAG"

if [[ "$PUSH" == "false" ]]; then
    echo ""
    echo "🚀 To run the container:"
    echo "   docker run --rm -it \\"
    echo "     -e KEENMAIL_API_KEY=your_key \\"
    echo "     -e KEENMAIL_SECRET=your_secret \\"
    echo "     $IMAGE_NAME:$TAG"
    echo ""
    echo "🐙 To push to registry:"
    echo "   $0 --push --tag $TAG"
fi
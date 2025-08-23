#!/bin/bash
set -euo pipefail

# KeenMail MCP Server - Publishing Script
# Usage: ./scripts/publish.sh [--dry-run] [--version patch|minor|major|X.Y.Z]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Default values
DRY_RUN=false
VERSION_BUMP=""
SKIP_TESTS=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --version)
            VERSION_BUMP="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run              Show what would be published without actually publishing"
            echo "  --version VERSION      Bump version: patch|minor|major|X.Y.Z"
            echo "  --skip-tests           Skip running tests before publishing"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --version patch --dry-run    # Test patch version bump"
            echo "  $0 --version 1.0.0              # Set specific version and publish"
            echo "  $0 --dry-run                    # Test current version publish"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🚀 KeenMail MCP Server Publishing Script${NC}"
echo "======================================"

# Check if we're in a git repo and on the right branch
if git rev-parse --git-dir > /dev/null 2>&1; then
    CURRENT_BRANCH=$(git branch --show-current)
    if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "uvx-package" ]]; then
        echo -e "${YELLOW}⚠️  Warning: Not on main or uvx-package branch (current: $CURRENT_BRANCH)${NC}"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${RED}❌ Uncommitted changes detected${NC}"
        echo "Please commit or stash your changes before publishing."
        exit 1
    fi
fi

# Get current version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo -e "${BLUE}📋 Current version: $CURRENT_VERSION${NC}"

# Version bumping
if [[ -n "$VERSION_BUMP" ]]; then
    echo -e "${BLUE}📈 Bumping version...${NC}"
    
    if [[ "$VERSION_BUMP" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        # Specific version provided
        NEW_VERSION="$VERSION_BUMP"
        # Update pyproject.toml manually for specific versions
        sed -i.bak "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
        rm pyproject.toml.bak
    else
        # Use uv version command for semantic bumping
        source ~/.local/bin/env 2>/dev/null || true
        NEW_VERSION=$(uv version "$VERSION_BUMP" --dry-run 2>/dev/null | grep "Would set version to" | cut -d' ' -f5 || echo "")
        
        if [[ -z "$NEW_VERSION" ]]; then
            echo -e "${RED}❌ Failed to determine new version${NC}"
            exit 1
        fi
        
        uv version "$VERSION_BUMP"
    fi
    
    echo -e "${GREEN}✅ Version bumped: $CURRENT_VERSION → $NEW_VERSION${NC}"
    CURRENT_VERSION="$NEW_VERSION"
fi

# Run tests unless skipped
if [[ "$SKIP_TESTS" != "true" ]]; then
    echo -e "${BLUE}🧪 Running tests...${NC}"
    source ~/.local/bin/env 2>/dev/null || true
    
    if ! uv run python -m pytest tests/ -v; then
        echo -e "${RED}❌ Tests failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All tests passed${NC}"
fi

# Build the package
echo -e "${BLUE}🔨 Building package...${NC}"
source ~/.local/bin/env 2>/dev/null || true

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

if ! uv build; then
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Package built successfully${NC}"
echo "Built files:"
ls -la dist/

# Check package contents
echo -e "${BLUE}📦 Package contents:${NC}"
tar -tzf dist/keenmail_mcp_server-${CURRENT_VERSION}.tar.gz | head -20

# Dry run check
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YELLOW}🧪 DRY RUN MODE - Not actually publishing${NC}"
    echo ""
    echo "Would publish:"
    echo "  - keenmail_mcp_server-${CURRENT_VERSION}.tar.gz"
    echo "  - keenmail_mcp_server-${CURRENT_VERSION}-py3-none-any.whl"
    echo ""
    echo "To PyPI as: keenmail-mcp-server==$CURRENT_VERSION"
    echo ""
    echo "After publishing, users can install with:"
    echo "  uvx keenmail-mcp-server"
    echo "  pip install keenmail-mcp-server"
    exit 0
fi

# Check for PyPI token
if [[ -z "${UV_PUBLISH_TOKEN:-}" ]]; then
    echo -e "${RED}❌ UV_PUBLISH_TOKEN environment variable not set${NC}"
    echo "Please set your PyPI API token:"
    echo "  export UV_PUBLISH_TOKEN='pypi-your-token-here'"
    echo ""
    echo "Or create ~/.config/uv/config.toml with:"
    echo "  publish-token = 'pypi-your-token-here'"
    exit 1
fi

# Final confirmation
echo -e "${YELLOW}⚠️  Ready to publish keenmail-mcp-server==$CURRENT_VERSION to PyPI${NC}"
echo ""
read -p "Are you sure you want to publish? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Publishing cancelled."
    exit 1
fi

# Publish to PyPI
echo -e "${BLUE}📤 Publishing to PyPI...${NC}"

if uv publish; then
    echo ""
    echo -e "${GREEN}🎉 Successfully published keenmail-mcp-server==$CURRENT_VERSION${NC}"
    echo ""
    echo "🔗 Package URL: https://pypi.org/project/keenmail-mcp-server/$CURRENT_VERSION/"
    echo ""
    echo "📥 Users can now install with:"
    echo "  uvx keenmail-mcp-server"
    echo "  pip install keenmail-mcp-server"
    echo ""
    
    # Create git tag if we're in a git repo and version was bumped
    if [[ -n "$VERSION_BUMP" ]] && git rev-parse --git-dir > /dev/null 2>&1; then
        TAG_NAME="v$CURRENT_VERSION"
        echo -e "${BLUE}🏷️  Creating git tag: $TAG_NAME${NC}"
        git add pyproject.toml
        git commit -m "Bump version to $CURRENT_VERSION"
        git tag "$TAG_NAME"
        
        echo -e "${YELLOW}📤 Don't forget to push the tag:${NC}"
        echo "  git push origin main --tags"
    fi
else
    echo -e "${RED}❌ Publishing failed${NC}"
    exit 1
fi
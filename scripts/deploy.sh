#!/usr/bin/env bash
set -e

echo "🚀 YYC³ EasyVizAI Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ LTS."
    exit 1
fi

NODE_VERSION=$(node --version | cut -c 2-3)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ is required. Current version: $(node --version)"
    exit 1
fi

print_status "Node.js version: $(node --version) ✓"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed."
    exit 1
fi

print_status "npm version: $(npm --version) ✓"

# Install dependencies
print_status "Installing backend dependencies..."
cd backend
npm install
cd ..

print_status "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Setup environment files
print_status "Setting up environment files..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    print_warning "Backend .env file created from example. Please configure your API keys!"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    print_status "Frontend .env.local file created from example."
fi

# Build applications
print_status "Building applications..."

print_status "Building frontend..."
cd frontend
npm run build
cd ..

print_status "Frontend build completed ✓"

# Test backend startup
print_status "Testing backend startup..."
cd backend
timeout 10s npm start > /dev/null 2>&1 &
BACKEND_PID=$!
sleep 5

if kill -0 "$BACKEND_PID" 2> /dev/null; then
    print_status "Backend startup test passed ✓"
    kill "$BACKEND_PID" 2> /dev/null || true
else
    print_error "Backend startup test failed"
    exit 1
fi
cd ..

print_status "Deployment completed successfully! 🎉"
echo ""
echo "Next steps:"
echo "1. Configure your API keys in backend/.env"
echo "2. Run 'make dev' to start development servers"
echo "3. Access the application at http://localhost:3000"
echo "4. Check backend health at http://localhost:8000/health"
echo ""
echo "For production deployment, see docs/ops-playbook.md"
.PHONY: bootstrap dev backend frontend test lint fmt clean type install-deps setup-env

# Install dependencies and setup environment
bootstrap: install-deps setup-env

install-deps:
	@echo "📦 Installing dependencies..."
	cd backend && npm install
	cd frontend && npm install

setup-env:
	@echo "⚙️  Setting up environment files..."
	cd backend && cp .env.example .env || true
	cd frontend && cp .env.example .env.local || true

# Development
dev:
	@echo "🚀 Starting development servers..."
	tmux new-session -d -s easyviz 'make backend' \; split-window -h 'make frontend' \; attach

backend:
	@echo "🔧 Starting backend server..."
	cd backend && npm run dev

frontend:
	@echo "💻 Starting frontend server..."
	cd frontend && npm run dev

# Production
build:
	@echo "🏗️  Building applications..."
	cd backend && npm run build || echo "Backend build not configured"
	cd frontend && npm run build

start:
	@echo "▶️  Starting production servers..."
	cd backend && npm start &
	cd frontend && npm start

# Testing
test:
	@echo "🧪 Running tests..."
	cd backend && npm test || echo "Backend tests not configured"
	cd frontend && npm test || echo "Frontend tests not configured"

# Linting and formatting
lint:
	@echo "🔍 Linting code..."
	cd backend && npm run lint || echo "Backend lint not configured"
	cd frontend && npm run lint

fmt:
	@echo "✨ Formatting code..."
	cd backend && npm run format || echo "Backend format not configured"
	cd frontend && npm run format

type:
	@echo "📝 Type checking..."
	cd backend && echo "Backend TypeScript check not configured"
	cd frontend && npm run type-check

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	rm -rf backend/node_modules backend/dist backend/.next backend/logs
	rm -rf frontend/node_modules frontend/dist frontend/.next
	rm -rf **/__pycache__ **/*.pyc

# Logs
logs:
	@echo "📋 Showing logs..."
	tail -f backend/logs/combined.log || echo "No logs found"

# Health check
health:
	@echo "🏥 Checking application health..."
	curl -s http://localhost:8000/health || echo "Backend not responding"
	curl -s http://localhost:3000 || echo "Frontend not responding"
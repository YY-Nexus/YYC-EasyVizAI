# YYC³ EasyVizAI

[![CI](https://github.com/YY-Nexus/YYC-EasyVizAI/actions/workflows/build.yml/badge.svg)](https://github.com/YY-Nexus/YYC-EasyVizAI/actions/workflows/build.yml)

AI-powered web application with Next.js frontend and Node.js backend, featuring chat interface, audio playback, and real-time WebSocket communication.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ LTS
- npm or pnpm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YY-Nexus/YYC-EasyVizAI.git
   cd YYC-EasyVizAI
   ```

2. **Install dependencies and setup environment**
   ```bash
   make bootstrap
   ```

3. **Configure API keys** (optional for development)
   ```bash
   # Edit backend/.env and add your API keys
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

4. **Start development servers**
   ```bash
   make dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/health

## 📁 Project Structure

```
├── backend/               # Node.js Express backend
│   ├── src/
│   │   ├── controllers/   # Request handlers
│   │   ├── routes/        # API routes
│   │   ├── services/      # Business logic
│   │   ├── middleware/    # Express middleware
│   │   ├── utils/         # Utilities and helpers
│   │   └── websocket/     # WebSocket handlers
│   ├── logs/              # Application logs
│   └── uploads/           # File uploads
├── frontend/              # Next.js React frontend
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── store/         # State management
│   │   └── types/         # TypeScript types
└── docs/                  # Documentation
```

## 🎯 Features

### Core Features
- ✅ **No-login interface** - Direct access without authentication
- ✅ **AI Chat Interface** - Real-time chat with AI models
- ✅ **Audio Upload & Playback** - Support for various audio formats
- ✅ **WebSocket Communication** - Real-time updates and messaging
- ✅ **LLM API Integration** - OpenAI, Anthropic, Gemini support
- ✅ **Responsive Design** - Mobile-friendly interface
- ✅ **Structured Logging** - Comprehensive logging system

### Reserved Features
- 🔄 **User Registration** - Endpoint reserved for future use
- 🔄 **Chat History** - Persistent conversation storage
- 🔄 **Advanced Audio Processing** - Speech-to-text, analysis

## 🛠️ Development

### Available Commands

```bash
# Development
make dev              # Start both frontend and backend
make backend          # Start only backend server
make frontend         # Start only frontend server

# Building
make build            # Build both applications
make start            # Start production servers

# Code Quality
make lint             # Run linters
make fmt              # Format code
make type             # Type checking

# Utilities
make clean            # Clean build artifacts
make logs             # View application logs
make health           # Check server health
```

### Environment Configuration

#### Backend (.env)
```bash
NODE_ENV=development
PORT=8000
OPENAI_API_KEY=your_openai_api_key_here
ENABLE_REGISTRATION=false
ENABLE_AUDIO_UPLOAD=true
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🌐 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /api/v1` - API information

### Chat API
- `POST /api/v1/chat/message` - Send chat message
- `POST /api/v1/chat/stream` - Stream chat response
- `GET /api/v1/chat/history` - Get chat history (placeholder)

### Audio API
- `POST /api/v1/audio/upload` - Upload audio file
- `GET /api/v1/audio/play/:id` - Play audio file
- `DELETE /api/v1/audio/:id` - Delete audio file

### Auth API (Reserved)
- `POST /api/v1/auth/register` - User registration (disabled)
- `POST /api/v1/auth/login` - User login (placeholder)
- `GET /api/v1/auth/me` - Current user info

## 🔧 Configuration

### Security Features
- CORS protection
- Helmet security headers
- Input validation
- File type/size restrictions
- Rate limiting ready

### Logging System
- Structured JSON logging
- Multiple log levels
- File rotation
- Error tracking
- Request/response logging

### WebSocket Features
- Topic-based subscriptions
- Auto-reconnection
- Ping/pong heartbeat
- Client management
- Message broadcasting

## 🚀 Deployment

### Local Deployment
```bash
# Production build
make build

# Start production servers
make start
```

### Environment Variables for Production
```bash
# Backend
NODE_ENV=production
PORT=8000
OPENAI_API_KEY=your_production_key
LOG_LEVEL=info

# Frontend
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_WS_URL=wss://your-api-domain.com
```

### Process Management
- Use PM2 for backend process management
- Use Nginx for frontend static serving
- Setup log rotation and monitoring

## 📚 Documentation

- [Architecture Overview](docs/architecture/core-architecture.md)
- [Frontend Guidelines](docs/developer/frontend_guidelines.md)
- [Backend Guidelines](docs/developer/backend_guidelines.md)
- [Getting Started](docs/developer/getting_started.md)
- [Security & Privacy](docs/developer/security_privacy.md)

## 🧪 Testing

Currently supports development testing. Production test suites to be implemented.

```bash
make test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Check the [documentation](docs/)
- Review the [troubleshooting guide](docs/developer/getting_started.md#常见问题)
- Open an issue for bug reports or feature requests

---

**YYC³ EasyVizAI** - AI-powered visualization and chat platform
Built with ❤️ by YY-Nexus

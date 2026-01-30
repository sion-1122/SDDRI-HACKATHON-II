# Todo List Hackathon Project

A modern full-stack task management application with AI chatbot integration, advanced features, and cloud-native architecture.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Status](https://img.shields.io/badge/status-In_Progress-yellow)
![License](https://img.shields.io/badge/license-MIT-orange)

## Project Overview

This is a hackathon project demonstrating modern full-stack development practices including:
- **Frontend**: Next.js 16 with React 19, TypeScript, Tailwind CSS 4, shadcn/ui
- **Backend**: FastAPI (Python) with PostgreSQL, AI chatbot integration
- **Infrastructure**: Kubernetes deployment with Minikube and Helm
- **Architecture**: Event-driven with Kafka and Dapr integration

## Current Status

### Completed Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | CLI TUI application (Python + Textual) |
| Phase 2 | ✅ Complete | MCP Server for prompts |
| Phase 3 | ✅ Complete | Frontend Task Manager (Next.js + shadcn/ui) |
| Phase 4 | ✅ Complete | AI Chatbot Integration (Natural Language) |
| Phase 5 | ✅ Complete | UX Improvements (Toast notifications, URL state) |
| Phase 6 | ✅ Complete | Intermediate Todo Features (Priority, Tags, Filters, Sort, Search) |
| Phase 7 | ✅ Complete | Kubernetes Deployment (Minikube + Helm) |

### Phase 8: Advanced Features (In Progress)

**Branch**: `008-advanced-features`

#### Completed
- ✅ Specification created

#### Pending
- ⏳ Due Dates with DateTime Picker (shadcn DatePicker)
- ⏳ Browser Notifications for Reminders
- ⏳ Recurring Tasks (daily/weekly/monthly)
- ⏳ Overdue task highlighting
- ⏳ Notification preferences UI

### Phase 9: Kafka Event Streaming (Spec Created)

**Branch**: `009-kafka-events`

#### Completed
- ✅ Specification created
- ✅ Minikube cluster started
- ✅ cert-manager installed for TLS

#### Pending
- ⏳ Redpanda Kafka deployment (failed - needs retry with adjusted resources)
- ⏳ Kafka topics creation (task-events, reminders, task-updates)
- ⏳ Event publishing from Chat API
- ⏳ Event consumers for reminders
- ⏳ Event schemas definition

### Phase 10: Dapr Integration (Spec Created)

**Branch**: `010-dapr-integration`

#### Completed
- ✅ Specification created

#### Pending
- ⏳ Dapr sidecar deployment
- ⏳ Pub/Sub over Kafka configuration
- ⏳ State management for conversations (Redis)
- ⏳ Cron bindings for reminders
- ⏳ Secrets management

### Phase 11: Cloud K8s Deployment (Spec Created)

**Branch**: `011-cloud-k8s-deployment`

#### Completed
- ✅ Specification created

#### Pending
- ⏳ Cloud cluster provisioning (AKS/GKE/OKE)
- ⏳ Container registry setup
- ⏳ Cloud Kafka deployment
- ⏳ CI/CD pipeline (GitHub Actions)
- ⏳ Monitoring & logging (Prometheus, Grafana, Loki)

## Quick Start

### Frontend Development

```bash
cd frontend
pnpm install
pnpm dev
```

Frontend runs on http://localhost:3000

### Backend Development

```bash
cd backend
uv sync
uv run uvicorn api.main:app --reload
```

Backend runs on http://localhost:8000

### Kubernetes Deployment (Local)

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=50gb

# Install Redis
helm install redis bitnami/redis --set architecture=standalone

# Build and load images
./k8s/scripts/build-and-load.sh

# Deploy app
helm install todo-app ./k8s/helm/todo-app
```

## Tech Stack

### Frontend
- **Next.js 16.1.1** - React framework with App Router
- **React 19.2.3** - UI library
- **TypeScript 5** - Type safety
- **Tailwind CSS 4** - Styling
- **shadcn/ui** - Component library
- **Sonner** - Toast notifications
- **nuqs** - URL state management
- **Better Auth 1.4.10** - Authentication

### Backend
- **Python 3.13+** - Runtime
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Neon PostgreSQL** - Database (serverless)
- **OpenAI API** - AI chatbot
- **WebSocket** - Real-time chat streaming

### Infrastructure
- **Docker** - Containerization
- **Minikube** - Local Kubernetes
- **Helm 3** - Package manager
- **Redpanda** - Kafka-compatible streaming
- **Dapr** - Distributed application runtime
- **Redis** - State store

## Features Implemented

### Core Features
- ✅ User authentication (login/register)
- ✅ Task CRUD operations
- ✅ Task status management (TODO, IN_PROGRESS, DONE)
- ✅ Task priority levels (HIGH, MEDIUM, LOW)
- ✅ Task tags management
- ✅ Multi-column filtering
- ✅ Multi-column sorting
- ✅ Full-text search
- ✅ Toast notifications (Sonner)
- ✅ URL state persistence (nuqs)

### AI Chatbot
- ✅ Natural language task creation
- ✅ Natural language task updates
- ✅ Real-time streaming responses
- ✅ WebSocket progress updates

### Deployment
- ✅ Docker containers for frontend and backend
- ✅ Kubernetes manifests (Deployments, Services, ConfigMaps)
- ✅ Helm charts for easy deployment
- ✅ Minikube local development

## Project Structure

```
todo-list-hackathon/
├── frontend/              # Next.js frontend application
│   ├── app/              # App Router pages
│   ├── components/       # React components (shadcn/ui)
│   └── lib/              # Utilities and API clients
├── backend/              # FastAPI backend application
│   ├── api/              # API endpoints
│   ├── models/           # SQLAlchemy models
│   ├── ai_agent/         # AI chatbot integration
│   └── core/             # Core configuration
├── k8s/                  # Kubernetes manifests
│   ├── helm/             # Helm charts
│   └── scripts/          # Deployment scripts
├── specs/                # Feature specifications (SDD)
│   ├── 001-todo-cli-tui/
│   ├── 002-mcp-server-prompts/
│   ├── 003-frontend-task-manager/
│   ├── 004-ai-chatbot/
│   ├── 005-ux-improvement/
│   ├── 006-k8s-deployment/
│   ├── 007-intermediate-todo-features/
│   ├── 008-advanced-features/     # Due dates, notifications, recurring
│   ├── 009-kafka-events/          # Event streaming
│   ├── 010-dapr-integration/      # Dapr sidecars
│   └── 011-cloud-k8s-deployment/  # Cloud deployment
└── cli/                  # Original CLI TUI application
```

## Development Workflow

This project uses **Spec-Driven Development (SDD)**:

1. **Specify** (`spec.md`) - Define requirements and acceptance criteria
2. **Plan** (`plan.md`) - Design architecture and components
3. **Tasks** (`tasks.md`) - Break down into actionable tasks
4. **Implement** - Write code following the plan

See `AGENTS.md` for detailed workflow guidelines.

## Environment Variables

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Backend (`.env`)
```env
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
```

## Testing

### Frontend
```bash
cd frontend
pnpm test
```

### Backend
```bash
cd backend
uv run pytest
```

## Deployment

### Vercel (Frontend)
Frontend is automatically deployed to Vercel on push to `main` branch.

### Kubernetes (Full Stack)
```bash
# Build and push images
./k8s/scripts/build-and-push.sh

# Deploy to cluster
helm upgrade --install todo-app ./k8s/helm/todo-app
```

## Contributing

1. Create a feature branch from `main`
2. Follow SDD workflow (spec → plan → tasks → implement)
3. Write tests for new features
4. Submit a Pull Request

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- [Next.js](https://nextjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Dapr](https://dapr.io/)
- [Redpanda](https://redpanda.com/)

---

**Version**: 2.0.0
**Status**: In Development (Phase 8-11)
**Last Updated**: January 2026

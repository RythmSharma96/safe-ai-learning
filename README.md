# JurneeGo Safe AI Learning Assistant

A child-safe AI learning assistant prototype. Children chat with an AI tutor, every message goes through safety screening, and teachers can review flagged conversations.

## Architecture Overview

- **Backend:** Django + DRF (Python 3.12)
- **Frontend:** React (Vite) + Tailwind CSS
- **Database:** PostgreSQL
- **AI:** OpenAI API (gpt-4o-mini) with mock adapter fallback
- **Safety:** Two-layer pipeline (keyword regex + OpenAI Moderation API)
- **Auth:** JWT (djangorestframework-simplejwt) with role-based access (learner/teacher/admin)

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Docker Compose

```bash
# Copy environment file and set your OpenAI key
cp .env.example .env
# Edit .env: set AI_ADAPTER=openai and OPENAI_API_KEY=sk-...

# Start all services
docker compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

On startup, the backend automatically runs migrations and seeds flag categories.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_ADAPTER` | `mock` | `"openai"` for real API, `"mock"` for development |
| `OPENAI_API_KEY` | | Required if AI_ADAPTER=openai |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `SAFETY_USE_OPENAI_MODERATION` | `true` | Enable OpenAI Moderation API as second safety layer |
| `DB_PASSWORD` | `localdev` | PostgreSQL password |
| `DJANGO_SECRET_KEY` | dev key | Change in production |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed frontend origins |

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup/` | Register (email, password, role, first_name, last_name) |
| POST | `/api/auth/login/` | Login, returns JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Current user profile |

### Conversations (Learner only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/conversations/` | Create conversation |
| GET | `/api/conversations/` | List own conversations |
| GET | `/api/conversations/{id}/` | Get conversation with messages |
| POST | `/api/conversations/{id}/messages/` | Send message, get AI response |

### Flagged Review (Teacher/Admin only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/conversations/flagged/` | List flagged conversations |
| GET | `/api/conversations/flagged/{id}/` | Flagged conversation with moderation details |

### Example API Calls

```bash
# Sign up as learner
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"kid@test.com","password":"testpass123","first_name":"Test","last_name":"Kid","role":"learner"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"kid@test.com","password":"testpass123"}'
# Returns: {"access": "eyJ...", "refresh": "eyJ..."}

# Create conversation (use access token from login)
curl -X POST http://localhost:8000/api/conversations/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Math help"}'

# Send message
curl -X POST http://localhost:8000/api/conversations/<conv_id>/messages/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"content":"What is 2 + 2?"}'
```

## Running Tests

```bash
cd backend
source venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.test python -m pytest -v       # All tests
DJANGO_SETTINGS_MODULE=config.settings.test python -m pytest safety/tests/ -v  # Safety tests only
```

## Project Structure

```
├── backend/
│   ├── accounts/       # Auth, User model, permissions
│   ├── conversations/  # Chat models, API, orchestration
│   ├── safety/         # Moderation pipeline, checkers, FlagCategory model
│   ├── ai/             # AI adapter interface (OpenAI + mock), prompt construction
│   └── config/         # Django settings (base/development/test)
├── frontend/
│   ├── src/pages/      # Login, Signup, Chat, Flagged dashboard
│   └── src/components/ # Reusable UI components
├── docker-compose.yml
└── .github/workflows/  # CI pipeline (lint, test, build)
```

## Assumptions

- This is a prototype; production needs secrets management, rate limiting, and monitoring and much more
- The keyword safety list is curated but not exhaustive; production needs ongoing maintenance
- JWT tokens stored in localStorage
- No email verification on signup
- No prompt injection defense beyond a soft instruction in the system prompt
- Learner age/grade not captured (system prompt assumes ages 6-14)

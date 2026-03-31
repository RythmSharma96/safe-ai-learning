# JurneeGo - Safe AI Learning Assistant Service

## Assignment Context

JurneeGo is building a child-safe AI learning product. This is a Founding Engineer home assignment to build a small prototype of a Safe AI Learning Assistant Service.

**Purpose:** Evaluate software engineering, DevOps and production readiness, AI engineering judgment, and ability to use AI as a high-leverage tool while retaining full ownership of the solution.

**What they evaluate:**
- Software engineering quality
- DevOps and production-readiness thinking
- AI engineering understanding
- Ability to use AI effectively without outsourcing engineering judgment to it
- Founder-level prioritization, ownership, and pragmatism

## Core User Flow

1. A learner starts a conversation
2. The learner sends a message (text-based)
3. The system generates an AI response
4. The conversation is stored
5. Unsafe or policy-sensitive interactions are flagged
6. A teacher or admin can review flagged conversations

## Functional Requirements

### 1) Backend API
- Create a conversation
- Send a message (and receive AI response)
- Retrieve conversation history
- List flagged conversations
- Retrieve a flagged conversation together with the reason it was flagged

### 2) AI Response Layer
- Use either a real LLM API or a mock adapter
- Isolate model access behind a clear interface/abstraction
- Construct prompts intentionally
- Handle model failures or timeouts reasonably

### 3) Safety / Policy Layer
Must check for at minimum:
- Self-harm or harm-related content
- Sexual or inappropriate content for minors
- Requests for personal contact information
- Manipulative or emotionally risky guidance

### 4) Persistence
Persist:
- Conversations
- Messages
- Moderation outcomes
- Flag reasons
- Useful metadata for review

### 5) DevOps / Local Environment
- Dockerfile(s)
- docker-compose or equivalent local startup
- Environment-variable configuration
- Clear local run instructions
- Basic CI pipeline for lint, test, and build
- Short note on evolving from local Docker Compose to staging/production (deployment, scaling, secrets, observability, rollback strategy)
- Optional: orchestration approach (e.g. Kubernetes) with reasoning and tradeoffs

### 6) Testing
- Unit tests for important business logic
- At least one safety-related test
- At least one integration-style test

## Non-Functional Expectations
- Clear structure and understandable abstractions
- Pragmatic design and explicit tradeoffs
- Sensible defaults and production awareness
- Minimal UI is fine; API-only is also acceptable if README and demo instructions are clear

## Required Deliverables

1. **Source code repository** - Full project with commit history intact
2. **README.md** - Setup instructions, local run steps, environment variables, test commands, example API calls or demo instructions, assumptions made
3. **ARCHITECTURE.md** (1-2 pages) - System design, key components and data flow, major tradeoffs, what was intentionally not built, how to evolve toward production, what to improve first with one more week
4. **AI_USAGE.md** - Which AI tools used, where AI helped, what AI generated that was useful, at least 2 examples of AI output that was wrong/weak/insecure/unsuitable, how those outputs were corrected/replaced, one example of explicitly rejected AI suggestion
5. **TRADEOFFS.md** - Remaining risks, intentional shortcuts, next engineering priorities
6. **Optional demo video** - 5-10 minute walkthrough (encouraged but not required)

## AI Usage Policy
AI tools are allowed and expected.

**Allowed:**
- AI coding assistants
- LLMs for brainstorming, scaffolding, refactoring, tests, and documentation
- Official documentation
- Normal developer research

**Not allowed:**
- Outsourcing the assignment to another person
- Submitting code or docs you do not understand
- Copy-pasting large unreviewed AI output without validating it
- Misrepresenting your contribution

Must be prepared to explain and defend all major architecture decisions, important code paths, why AI suggestions were accepted or rejected, and where the current design is still weak.

## Submission
- Submit repository link + required markdown documents + any demo link or video
- Commit history preferred (shows how solution evolved)
- Commit count not scored mechanically

## After Submission
Live review session: walk through system, discuss design decisions, talk through where AI helped and where it did not, review how to productionize the service further.

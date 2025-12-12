# BANK_ASSISTANCE_SUPPORT — Production-Grade AI Banking Assistant (RAG + Web Search + Memory + Traces)

A full-stack AI banking support assistant built like a real product: **intelligent routing**, **hybrid RAG**, **web search**, **conversation memory**, **citations**, and a **trace panel** so you can inspect how answers were produced.

This repo is intentionally **not** “just a prompt” or a notebook demo. It focuses on the missing 80%: **UX + routing decisions + observability + deployability + cost/latency/quality trade-offs**.

---

## Why this project

Most people get stuck at one of these points:
- They build a chatbot that answers, but can’t explain *why*.
- They add RAG, but retrieval is fragile and debugging is painful.
- They try web search, but short follow-ups become generic.
- They pay early for APIs before they even know the architecture is correct.

I built BANK_ASSISTANCE_SUPPORT with a **free-first / low-cost** approach so you can validate the system end-to-end before scaling up.  
Also: **Groq** (fast LLM inference) is *Groq*, not “Grok”.

---

## What it does

BANK_ASSISTANCE_SUPPORT can:
- Answer from **internal knowledge** (policies, FAQs, PDFs) via **RAG**
- Pull **fresh / time-sensitive info** via **web search**
- Combine both using **HYBRID** routing when needed
- Remember context via **Redis session memory**
- Provide **citations** + **trace view** (route decision + sources + context used)
- Prepare for “last mile support workflows” (roadmap):
  - finding the right person/team to contact
  - guided form filling
  - voice/calls execution support

---

## Key features

### 1) Frontend that feels like a real product
- React 18 + Vite chat UI
- Markdown answers + citation chips
- Trace / Explain drawer (route, sources, snippets, latency)
- Loading/error/retry states (not “happy path only”)

### 2) Intelligent query routing
Each query is routed into one mode:
- `RAG_ONLY` — internal knowledge base
- `SEARCH_ONLY` — temporal/current info (rates, latest changes)
- `HYBRID` — combine internal docs + web results
- `FORM_FILLING` — guided workflow and structured collection
- `ESCALATE` — sensitive requests / PII / needs human

### 3) RAG with hybrid retrieval
- Chunking + embeddings + Qdrant storage
- Hybrid scoring (vector + keyword + rerank)
- Metadata per chunk (source, page, chunk_id, tags) for traceability

### 4) Conversation memory (Redis)
- Session key pattern: `session:{session_id}`
- TTL cleanup (e.g., 3600 seconds)
- Enables natural follow-ups (“What about BNP?”)

### 5) Web search integration (Tavily) + optional agentic patterns
- Search is triggered when temporal intent is detected
- Query enrichment using conversation history
- Optional multi-step search orchestration (CrewAI patterns)

### 6) Engineering maturity (CI/CD + deployability)
- Dockerized services for reproducible runs
- CI pipeline hooks (lint/test/build)
- Environment-based configuration (dev/staging/prod ready)
- Designed to be portable across multiple clouds

---

## Architecture (high-level)

Request path:

    User (React UI)
        |
        v
    FastAPI Gateway  ---> Session Manager (Redis)
        |
        v
    Router (intent + safety + temporal detection)
        |                 |                 |
        v                 v                 v
    RAG Service       Web Search        Escalation / Form
    (Qdrant)          (Tavily)          (workflow)
          \              /
           \            /
            v          v
         LLM Answer (Groq) + Citations + Trace
                    |
                    v
            Store to Redis + Postgres

---

## Tech stack

Backend
- FastAPI (Python)
- Groq LLM API (fast inference)
- Tavily Search API
- Qdrant (vector DB)
- Redis (session memory)
- PostgreSQL (persistence/audit)
- Optional: CrewAI (agentic search flows)

Frontend
- React 18 + Vite
- Tailwind CSS
- Markdown rendering + citations UI

Infra / DevOps
- Docker + Docker Compose
- GitHub Actions (recommended CI/CD)

---

## Screenshots / demo (add these!)
These increase trust instantly (especially on LinkedIn):
- `docs/screenshots/chat.png` (chat UI + citations)
- `docs/screenshots/trace.png` (trace/explain panel)
- `docs/architecture.png` (architecture diagram)

Demo (optional):
- Live demo: <ADD_LINK>
- Short video: <ADD_LINK>

---

## Quickstart (free-first / low-cost)

This repo is designed so you can validate architecture before paying heavily.

Prereqs:
- Groq API key (LLM)
- Tavily API key (web search)

Steps:
1) Clone and create `.env`
2) Run services via Docker Compose
3) Open UI and test routes (RAG vs Search vs Hybrid)
4) Inspect trace view to debug and tune

---

## Run with Docker Compose (recommended)

1) Clone

    git clone https://github.com/mohsensoleimanis/BANK_ASSISTANCE_SUPPORT.git
    cd BANK_ASSISTANCE_SUPPORT

2) Create env file

    cp .env.example .env

3) Fill required variables in `.env`
- GROQ_API_KEY
- TAVILY_API_KEY

4) Start everything

    docker compose up --build

5) Open
- Frontend: http://localhost:3000  (or 5173 depending on your Vite config)
- Backend:  http://localhost:8000
- Qdrant:   http://localhost:6333

---

## Run locally (no Docker)

Backend

    cd backend
    python -m venv .venv
    source .venv/bin/activate     # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

Frontend

    cd frontend
    npm install
    npm run dev

---

## Environment variables

Create `.env` from `.env.example`.

Required
- GROQ_API_KEY=...
- TAVILY_API_KEY=...

Typical
- BACKEND_PORT=8000
- FRONTEND_PORT=3000
- REDIS_URL=redis://redis:6379
- POSTGRES_URL=postgresql://user:pass@postgres:5432/bank_assistant
- QDRANT_URL=http://qdrant:6333

Optional flags (recommended)
- ROUTER_STRICT_MODE=true|false
- ENABLE_AGENTIC_SEARCH=true|false
- TRACE_ENABLED=true|false
- MAX_HISTORY_TURNS=6
- SESSION_TTL_SECONDS=3600
- TOP_K=5

---

## Routing logic

The router decides how to answer every query.

Typical pseudo logic:

    if temporal_intent(query): SEARCH_ONLY
    elif sensitive_or_pii(query): ESCALATE
    elif internal_policy_intent(query): RAG_ONLY
    else: HYBRID

Why this matters:
- Makes the system reliable and cheaper (don’t web-search everything)
- Prevents unsafe handling of sensitive data
- Keeps answers grounded (docs first, search when needed)

---

## RAG pipeline

Ingestion
- Read docs (PDF/HTML/MD)
- Chunk into overlapping segments (example: 512 tokens with overlap)
- Embed chunks using sentence-transformers
- Store in Qdrant with metadata

Example Qdrant payload shape:

    {
      "id": "chunk_0142",
      "text": "…chunk text…",
      "source": "bank_policy.pdf",
      "page": 12,
      "chunk_id": "0142",
      "tags": ["savings", "rates", "eligibility"]
    }

Retrieval
- Vector similarity top candidates
- Keyword boost / rerank
- Return top K + metadata for citations and trace

---

## Web search + agentic search (CrewAI patterns)

Standard web search (Tavily) is used when:
- query has temporal intent: “today”, “latest”, “current”
- internal docs are missing/weak for that question
- route is HYBRID or SEARCH_ONLY

Query enrichment for short follow-ups:
- Follow-ups like “What about BNP?” get enriched using previous user topic
- This is critical to avoid generic web results

Agentic search (optional):
- Multi-step search planning (several targeted queries)
- Source filtering and synthesis
- Still traced and inspectable

Note: Agentic search is powerful, but should be evaluated and rate-limited like any production capability.

---

## Conversation memory (Redis)

Key pattern:
- session:{session_id}

Stored data:
- List of JSON messages (role + content)
- TTL expiration for cleanup

Why Redis:
- Extremely fast access (sub-millisecond typical)
- Clean TTL support
- Scales well for many concurrent sessions

---

## Citations + trace panel (inspectability)

This project prioritizes “show your work”:
- Which route was used (RAG vs Search vs Hybrid)
- Which chunks were retrieved (source/page/chunk_id/score)
- Which web sources were used
- How much latency each stage took (optional)
- A high-level view of how the prompt/context was assembled

This makes failures fixable:
- Empty retrieval → adjust chunking/rerank/metadata
- Bad search results → improve enrichment/filtering
- Uncertain answer → escalate or ask clarification

---

## Observability & debugging

Recommended logging fields (even if minimal):
- request_id / session_id
- route_type
- retrieved_chunks_count
- web_sources_count
- latencies per stage
- error type (retrieval empty, search timeout, LLM error)

Future-friendly span names (OpenTelemetry style):
- api_receive
- redis_load
- router
- qdrant_retrieve
- web_search
- llm_generate
- store_response

---

## CI/CD

This repo is CI-ready. A typical pipeline includes:
- Backend: formatting + lint + unit tests
- Frontend: lint + build
- Docker image build (optional but recommended)

Example GitHub Actions workflow outline (adapt paths/commands to your repo):

    name: CI

    on:
      push:
        branches: [ "main" ]
      pull_request:

    jobs:
      backend:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: "3.11"
          - name: Install backend deps
            run: |
              cd backend
              pip install -r requirements.txt
          - name: Backend tests
            run: |
              cd backend
              pytest -q

      frontend:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-node@v4
            with:
              node-version: "20"
          - name: Install frontend deps
            run: |
              cd frontend
              npm ci
          - name: Build frontend
            run: |
              cd frontend
              npm run build

---

## Security notes

Important:
- NEVER commit real secrets (.env)
- Keep `.env` in `.gitignore`
- Prefer server-side calls to external APIs (do not expose keys in frontend)
- Consider basic controls even for demos:
  - input validation
  - rate limiting
  - safe logging (no PII)
  - escalation on sensitive prompts

---

## Multi-cloud / portability

The project is designed so the same architecture can run across different environments:
- local dev (Docker Compose)
- a single VM (Docker)
- container platforms (Kubernetes-ready)
- different cloud providers with minimal changes

Goal: avoid vendor lock-in while still keeping production patterns.

---

## Roadmap

Planned next steps:
- User authentication
- Form filling assistant (guided workflows + validation)
- Voice interface / calling support
- Multi-language support
- Analytics dashboard
- A/B testing framework (routing, retrieval, prompt trade-offs)
- Deeper evaluation suite (quality + cost + latency)

---

## Project structure (recommended)

    BANK_ASSISTANCE_SUPPORT/
      backend/
      frontend/
      infra/
        docker-compose.yml
      docs/
        architecture.png
        screenshots/
      .github/
        workflows/
          ci.yml
      .env.example
      .gitignore
      README.md
      LICENSE

---

## FAQ

Q: Is this a real banking product?
A: No. This is a technical project demonstrating production patterns for support assistants (routing, RAG, search, memory, tracing).

Q: Why Groq + Tavily?
A: Fast iteration. Many builders get stuck at “should I pay?” early. This setup helps validate the architecture first.

Q: Can I swap providers?
A: Yes. The design is modular: LLM provider and search provider can be replaced behind clean interfaces.

---

## Contributing

PRs and issues are welcome.
If you contribute:
- keep changes modular (router/search/rag/memory)
- add tests for core behavior
- keep traceability intact (citations + trace view)

---

## License
MIT

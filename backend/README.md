# Bank Support AI - Backend

FastAPI backend with RAG, LLM, and web search integration.

## Quick Start

1. **Setup environment**:
   ```powershell
   .\setup.ps1
   ```

2. **Activate virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   - Edit `.env` file
   - Add your `GROQ_API_KEY` and `TAVILY_API_KEY`

5. **Start services** (Postgres, Redis, Qdrant):
   ```bash
   cd ..
   docker-compose up -d
   ```

6. **Ingest sample documents**:
   ```bash
   python scripts/ingest_documents.py --path ../data/documents/policies
   ```

7. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Access API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/api/v1/health

## API Endpoints

### Chat
- `POST /api/v1/chat/` - Send message and get AI response
- `GET /api/v1/chat/history/{session_id}` - Get conversation history
- `DELETE /api/v1/chat/session/{session_id}` - Clear session

### Health
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health check

## Testing

Test the chat endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your savings account rates?"}'
```

## Project Structure

```
app/
├── api/v1/routes/     # API endpoints
├── core/              # Core AI components
│   ├── llm/          # LLM integration
│   ├── rag/          # RAG components
│   ├── search/       # Web search
│   └── orchestrator/ # Main agent logic
├── models/           # Pydantic models
├── services/         # Business logic
└── utils/            # Utilities
```

## Environment Variables

Required:
- `GROQ_API_KEY` - Groq API key
- `TAVILY_API_KEY` - Tavily search API key

Optional:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `VECTOR_DB_URL` - Qdrant URL

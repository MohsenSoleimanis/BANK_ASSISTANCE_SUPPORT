# Bank Support AI

AI-powered bank support system with RAG, web search, and form filling capabilities.

## Features

- 🤖 Intelligent chat support powered by Groq LLM
- 📚 RAG (Retrieval Augmented Generation) with vector database
- 🔍 Web search integration via Tavily API
- 📝 Interactive form filling assistant
- 🔒 Security-first design for banking applications

## Quick Start

### Backend

1. Create virtual environment:
```
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up environment variables:
```
cp .env.example .env
# Edit .env with your API keys
```

4. Run the server:
```
uvicorn app.main:app --reload
```

### Frontend

1. Install dependencies:
```
cd frontend
npm install
```

2. Run development server:
```
npm run dev
```

### Using Docker

```
docker-compose up
```

## Project Structure

See docs/ARCHITECTURE.md for detailed architecture documentation.

## Development

Run tests:
```
pytest backend/tests/ -v --cov
```

## License

MIT
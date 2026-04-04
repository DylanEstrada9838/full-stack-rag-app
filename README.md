# RAG App — Reglamento Tec de Monterrey

A full-stack Q&A chat application powered by a Retrieval-Augmented Generation (RAG) pipeline. Ask questions about the **Reglamento General de Estudiantes** and get contextual answers from an LLM.

```
rag-app/
├── backend/         # FastAPI + RAG pipeline
│   ├── main.py      # API server (endpoints: /health, /ask)
│   ├── rag_pipeline/ # Chunking, vectorstore, retriever, LLM chain
│   └── requirements.txt
├── frontend/        # React (Vite) chat UI
│   ├── src/
│   │   ├── App.jsx          # Main chat component
│   │   ├── App.css          # Blue-themed styles
│   │   └── components/
│   │       └── ChatMessage.jsx
│   └── package.json
└── README.md        # This file
```

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Ollama** installed and running with `llama3` model:
  ```bash
  ollama run llama3
  ```

---

## Quick Start

### 1. Backend

```bash
# Navigate to backend
cd rag-app/backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Create environment file
cp .env.example .env
# (Optional) Open .env and add your HF_TOKEN if needed

# Install dependencies
pip install -r requirements.txt

# --- IMPORTANT: Initialize/Build the vector database ---
# The database is not included in git. Build it from the PDF:
python rebuild_db.py

# Start the API server
uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**.  
Test it: open **http://localhost:8000/health** in your browser.

### 2. Frontend

Open a **new terminal**:

```bash
# Navigate to frontend
cd rag-app/frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at **http://localhost:5173**.

---

## API Endpoints

| Method | Endpoint  | Description |
|--------|-----------|-------------|
| GET    | `/health` | Health check |
| POST   | `/ask`    | Send a question, get an answer + source pages |

### Example request:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué implica la baja definitiva?"}'
```

### Example response:

```json
{
  "answer": "La baja definitiva implica la exclusión permanente del estudiante...",
  "sources": [47, 51]
}
```

---

## Next Steps & Recommendations

### Short-term Improvements
1. **Streaming responses** — Use FastAPI's `StreamingResponse` + LangChain's `.stream()` to show the answer word-by-word instead of waiting for the full response.
2. **Chat history** — Store conversation context so the LLM can handle follow-up questions naturally.
3. **Error handling** — Add detailed error messages, retry logic, and loading timeouts on the frontend.
4. **Dark mode** — Add a toggle button; the CSS variables make this easy to implement.

### Production Readiness
5. **Containerize** — Create `Dockerfile` for backend and frontend, and a `docker-compose.yml` to start everything with one command.
6. **Authentication** — Add user login (JWT tokens) so only authorized users can access the system.
7. **Database for chat history** — Store conversations in PostgreSQL or MongoDB for persistence.
8. **Cloud deployment** — Deploy the backend to AWS/GCP/Azure and the frontend to Vercel or Netlify.
9. **Rate limiting** — Protect the API from abuse with rate limiting middleware.
10. **Monitoring** — Add logging (e.g., structured JSON logs) and connect to an observability tool like Grafana or Datadog.

### RAG Pipeline Enhancements
11. **Better embeddings** — Try multilingual models like `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` since the documents are in Spanish.
12. **Upgrade LLM** — Use a more powerful model via Ollama (e.g., `llama3.1:70b` or `mistral`) or connect to OpenAI/Claude API.
13. **Multi-document support** — Extend the pipeline to handle multiple PDFs or regulation documents.
14. **Feedback loop** — Let users rate answers (👍/👎) and use that data to improve retrieval.

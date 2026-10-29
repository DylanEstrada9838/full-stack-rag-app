# RAG App — Reglamento Universitario

A production-ready full-stack Retrieval-Augmented Generation (RAG) assistant for university regulations (**Reglamento General de Estudiantes**), featuring sub-second hybrid retrieval, OpenAI inference, and live execution telemetry.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://full-stack-rag-app-beta.vercel.app/)
[![Backend API](https://img.shields.io/badge/API-Azure_Container_Apps-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://rag-backend.happypond-8a46921f.spaincentral.azurecontainerapps.io/health)

* 🌐 **Frontend (Vercel):** [full-stack-rag-app-beta.vercel.app](https://full-stack-rag-app-beta.vercel.app/)
* ⚙️ **Backend API (Azure Container Apps):** [rag-backend.happypond-8a46921f.spaincentral.azurecontainerapps.io](https://rag-backend.happypond-8a46921f.spaincentral.azurecontainerapps.io/health)

---

## ⚡ Highlights

* **Serverless Architecture:** Decoupled React (Vite) client on Vercel and a containerized FastAPI backend on **Azure Container Apps** (Spain Central) with automated **GitHub Actions CI/CD**.
* **Ultra-Fast Hybrid Retrieval (~0.06s):** Dense vector search via **FastEmbed ONNX** (`BAAI/bge-small-en-v1.5` in ChromaDB) + pre-cached lexical search (**Rank-BM25**).
* **OpenAI Responses API:** Strict context-grounded inference using `client.responses.create(model="gpt-4.1-mini")`.
* **Real-Time Telemetry:** Live chat UI displays retrieval and model latencies in seconds, with a hoverable `+ Info` popover showing token usage (in/out) and estimated query cost.

---

## 🧠 Pipeline Architecture

```text
[ Query ] ──► Hybrid Search (Dense MMR + Sparse BM25) ──► Top 5 Chunks (0.06s)
                                                                 │
[ OpenAI Responses API ] ◄── Prompt Contextualization ───────────┘
     (gpt-4.1-mini)
           │
           ▼
[ Answer + Telemetry: Dual Latencies, Tokens, Cost & Chunks Drawer ]
```

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite, Vanilla CSS | Single-page chat UI with telemetry pills, hover popover, and chunks drawer |
| **Backend API** | FastAPI, Uvicorn, Pydantic | Asynchronous REST service with CORS and error handling |
| **LLM Inference** | OpenAI Responses API | `gpt-4.1-mini` via official OpenAI SDK |
| **Embeddings** | FastEmbed ONNX | CPU-optimized `bge-small-en-v1.5` embeddings without PyTorch overhead |
| **Vector & Keyword Store** | ChromaDB + Rank-BM25 | Persistent vectorstore and pre-cached sparse index |
| **Cloud Hosting** | Azure Container Apps + Vercel | Scalable container service (Azure) and edge CDN (Vercel) |

---

## 📡 API Endpoints

### `POST /ask`
Submit a question (3–500 characters) and receive an answer with telemetry and source chunks:

```bash
curl -X POST https://rag-backend.happypond-8a46921f.spaincentral.azurecontainerapps.io/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuáles son las faltas disciplinarias?"}'
```

**Response (Sample):**
```json
{
  "answer": "Las faltas disciplinarias son todos aquellos hechos individuales o colectivos que desvirtúen...",
  "latency": 3.86,
  "retrieval_sec": 0.06,
  "llm_sec": 3.80,
  "input_tokens": 412,
  "output_tokens": 128,
  "total_cost": 0.000499,
  "model": "gpt-4.1-mini-2025-04-14",
  "chunks": [ ... ]
}
```

---

## 🚀 Quick Start (Local)

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows (or: source venv/bin/activate)
pip install -r requirements.txt
# Set OPENAI_API_KEY in backend/.env
python rebuild_db.py           # First time only: builds Chroma & BM25 cache
uvicorn main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev                    # Runs on http://localhost:5173
```

---

## 📁 Repository Structure

```text
rag-app/
├── .github/
│   └── workflows/
│       └── deploy-backend-azure.yml # CI/CD deployment to Azure Container Apps
├── backend/                         # FastAPI backend service
│   ├── rag_pipeline/                # Chunking, vectorstore, retriever, OpenAI chain
│   │   ├── documents/               # Source PDF regulation documents
│   │   ├── prompts/                 # Prompt templates (v1.txt, v2.txt)
│   │   ├── chroma_db/               # Pre-built Chroma vectorstore
│   │   └── bm25_retriever.pkl       # Pre-cached BM25 lexical index
│   ├── Dockerfile                   # Production Dockerfile
│   ├── main.py                      # FastAPI server entry point
│   ├── config.py                    # Environment & CORS configuration
│   ├── routes.py                    # API route endpoints
│   ├── models.py                    # Pydantic request/response schemas
│   ├── rebuild_db.py                # Database build & caching script
│   └── requirements.txt             # Python dependencies
├── frontend/                        # React (Vite) client application
│   ├── src/
│   │   ├── components/              # ChatMessage, Header, ChunksPanel, WelcomeCard
│   │   ├── constants/               # Suggested questions
│   │   ├── App.jsx                  # Main application orchestrator
│   │   └── App.css                  # UI styling, responsive layout & popover
│   └── package.json                 # Node.js dependencies
├── AZURE_DEPLOYMENT_SUMMARY.md      # Azure CLI & deployment log
└── README.md
```

---

## 👨‍💻 Author

**Dylan Estrada** · *Asistido por Gemini 3.8 y Claude Sonnet 4.6*  
💼 [LinkedIn](https://www.linkedin.com/in/dylan-estrada-606691216/) · 🐙 [GitHub](https://github.com/DylanEstrada9838)

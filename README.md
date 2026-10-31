# Full-Stack RAG Application

A full-stack Retrieval-Augmented Generation (RAG) application
that enables users to interact with institutional documents
through a conversational AI interface.

The application combines semantic and keyword-based retrieval,
hybrid search, reranking, and LLM-powered generation to provide
relevant, context-grounded answers.

Built with React, FastAPI, LangChain, ChromaDB, and OpenAI.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://full-stack-rag-app-beta.vercel.app/)

🌐 **Live Application:** [https://full-stack-rag-app-beta.vercel.app/](https://full-stack-rag-app-beta.vercel.app/)

---

## 📸 UI Preview

![Application UI](./assets/rag-app.png)

---

## ✨ Key Features

- Conversational AI interface for querying institutional documents.
- Hybrid retrieval combining dense semantic search and sparse BM25.
- Maximal Marginal Relevance (MMR) for diverse document retrieval.
- Context-grounded generation using OpenAI Responses API.
- Real-time response streaming using Server-Sent Events (SSE).
- Retrieval and generation telemetry, including latency and token usage.
- Docker-based containerization and automated CI/CD.
- Cloud deployment using Azure Container Apps and Vercel.

## 🧠 RAG & Pipeline Architecture

The core of this AI project is an end-to-end hybrid RAG pipeline featuring efficient document retrieval and streaming LLM generation, engineered for precision and factual grounding against academic regulatory documents. The diagram below illustrates the high-level architecture and interactions between the presentation layer, API layer, RAG retrieval engine, and cloud services:

![RAG App System Architecture](./assets/rag_app_system_architecture.png)

### 1. Orchestration Framework
* **LangChain**: Orchestrates the document loading, splitting, vectorstore indexing, ensemble retrieval (`EnsembleRetriever`), and prompt pipelines.

---

### 2. Chunking Strategy
* **Splitter**: `RecursiveCharacterTextSplitter`
* **Chunk Size**: `512` characters
* **Chunk Overlap**: `128` characters
* **Design Rationale**: A 512-character window preserves atomic legal and regulatory articles without diluting semantic meaning. The 128-character overlap guarantees that legal qualifications, exceptions, and procedural clauses spanning chunk boundaries maintain contiguous context.

---

### 3. Embedding Model
* **Model**: `sentence-transformers/all-MiniLM-L6-v2`
* **Inference Engine**: **FastEmbed ONNX Runtime** (CPU-optimized)
* **Key Advantages & Production Considerations**:
  * **Embedding Generation Time**: Efficient CPU inference powered by ONNX Runtime without requiring dedicated GPU infrastructure.
  * **Memory Consumption (RAM)**: Lean memory footprint suitable for resource-constrained cloud containers, avoiding heavy PyTorch runtime overhead.
  * **Docker Image Size**: Substantially smaller container image by omitting PyTorch and CUDA runtime dependencies.
  * **API Response Latency**: Fast, consistent query encoding that minimizes retrieval overhead.

---

### 4. Hybrid Retrieval Engine
Combines semantic understanding (dense vectors) with exact legal terminology matching (sparse lexical search):

* **Vector Database**: **ChromaDB** (persistent on disk with cosine distance).
* **Dense Vector Search (60% weight)**:
  * **Maximal Marginal Relevance (MMR)**: Balances two competing objectives:
    1. *Relevance*: Retrieves documents most semantically similar to the user's question.
    2. *Diversity*: Penalizes redundant chunks to ensure varied, non-repetitive legal contexts.
  * *Parameters*: Initially retrieves `fetch_k = 20` candidates and filters down to the `5` most diverse, useful chunks.
* **Sparse Lexical Search (40% weight)**:
  * **Rank-BM25**: Keyword-frequency matching optimized for exact article numbers, penalties, infractions, and specialized academic terms.
  * Pre-cached via serialized binary index (`bm25_retriever.pkl`) to avoid re-indexing during startup.
  * Retrieves `5` keyword-matched candidates.
* **Ensemble Retrieval & Weighted Reciprocal Rank Fusion (RRF)**:
  LangChain's `EnsembleRetriever` merges and re-ranks candidate documents from both retrievers using weighted Reciprocal Rank Fusion (RRF):
  ```python
  EnsembleRetriever(
      retrievers=[vec_retriever, bm25_retriever],
      weights=[0.6, 0.4],
  )
  ```
  * `0.6` (60% weight): Dense MMR retriever — prioritizes semantic meaning, synonyms, and conceptual intent.
  * `0.4` (40% weight): Sparse BM25 retriever — boosts exact article numbers, penalties, and legal terminology.
  * Formula: $\text{RRF Score}(d) = 0.6 \cdot \frac{1}{\text{rank}_{\text{dense}}(d) + 60} + 0.4 \cdot \frac{1}{\text{rank}_{\text{bm25}}(d) + 60}$
  * The top 5 highest-scoring ground-truth chunks are passed directly into the LLM context.

---

### 5. LLM Model & Generation Layer
* **Model**: OpenAI `gpt-4.1-mini` via the official OpenAI Responses API.
* **Context & Prompt Grounding**: Context injected directly into system instructions, enforcing strict adherence to provided articles and reducing hallucinations.
* **Prompt Versioning**: Systematic prompt templates managed in `backend/rag_pipeline/prompts/` (e.g. `v1.txt`, `v2.txt`), allowing prompt updates via the `RAG_PROMPT_FILE` environment variable without code modifications.
* **Real-Time Token Streaming**:
  * **Server-Sent Events (SSE)**: Streams text deltas in real-time (`response.output_text.delta`), displaying a progressive typewriter effect in the frontend as tokens are generated.
* **Full Telemetry & Metrics**:
  * **Time to First Token (TTFT)**: Measured and exposed in the telemetry payload.
  * **Dual Latencies**: Retrieval time vs. Model generation time tracked independently to 2 decimal places.
  * **Input & Output Tokens**: Exact token counts (including cached input token recognition).
  * **Cost Estimation**: Dynamic per-query cost calculation based on actual token usage ($0.40/1M uncached input, $0.10/1M cached input, $1.60/1M output).

---

### 6. API Layer
* **FastAPI**: Asynchronous Python web framework with auto-generated OpenAPI documentation.
* **Pydantic**: Robust data validation and schema enforcement for requests (`QuestionRequest`) and responses (`AnswerResponse`).
* **Uvicorn**: High-performance ASGI server.
* **Protocol**: Dual-mode HTTP REST API supporting both standard JSON requests and Server-Sent Events (`text/event-stream`).
* **Cloud Runtime**: Containerized and hosted on **Azure Container Apps** (Spain Central).

---

### 7. Presentation Layer
* **React 19 & Vite**: Fast, lightweight client-side application.
* **Responsive Design**: Custom Vanilla CSS with mobile-first layout, glassmorphism, blinking streaming cursor, and slide-out bottom sheet chunk inspector.
* **Live Telemetry UI**: Direct visual badges for Retrieval & Model durations, with a hoverable `+ Info` popover detailing TTFT, token usage, and query cost.
* **Hosting**: Deployed globally via **Vercel Edge Network**.

---

### 8. DevOps & CI/CD
* **Docker Containerization**: Production multi-layer Docker image with pre-warmed vectorstore and pre-cached BM25 index generated during build time.
* **GitHub Actions Workflow**: Automated CI/CD pipeline triggered on pushes to `main`.
* **Container Registry**: Automated image build and push to **Azure Container Registry (ACR)**.
* **Cloud Infrastructure**: Scalable container execution on **Azure Container Apps** with environment secret management.


---

## 🚀 Getting Started (Running Locally)

You can run the application locally using either **Docker Compose** (recommended for an isolated setup) or by running the **Backend & Frontend natively**.

### 1. Prerequisites

* [Git](https://git-scm.com/)
* [OpenAI API Key](https://platform.openai.com/api-keys)
* **For Docker Compose**: [Docker Desktop](https://www.docker.com/) (version 20.10+) & Docker Compose
* **For Native Execution**:
  * [Python 3.11+](https://www.python.org/)
  * [Node.js 18+](https://nodejs.org/) & `npm`

---

### 2. Environment Variables

Create your environment configuration by copying the example template:

```bash
# Root environment (used by Docker Compose)
cp .env.example .env

# Or for native backend development
cp backend/.env.example backend/.env
```

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `OPENAI_API_KEY` | **Yes** | — | OpenAI API key for `gpt-4.1-mini` inference |
| `OPENAI_MODEL` | No | `gpt-4.1-mini` | OpenAI model identifier |
| `RAG_PROMPT_FILE` | No | `v2.txt` | Prompt template from `rag_pipeline/prompts/` |
| `HF_TOKEN` | No | — | HuggingFace Hub token (optional) |
| `EXTRA_CORS_ORIGINS`| No | — | Comma-separated list of allowed origins |

---

### 3. Option A: Run with Docker Compose (Recommended)

Build and launch both the backend API and frontend reverse-proxy containers in one command:

```bash
# 1. Clone repository
git clone https://github.com/DylanEstrada9838/full-stack-rag-app.git
cd full-stack-rag-app

# 2. Configure environment (set your OPENAI_API_KEY in .env)
cp .env.example .env

# 3. Build and launch services
docker compose up --build
```

* **Frontend UI**: [http://localhost:3000](http://localhost:3000)
* **Backend API**: [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 4. Option B: Native Execution

#### Step 1 — Backend (FastAPI)
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables in backend/.env
cp .env.example .env

# Build ChromaDB vectorstore and BM25 cache (first time only)
python rebuild_db.py

# Start development server
uvicorn main:app --reload --port 8000
```

#### Step 2 — Frontend (React + Vite)
In a separate terminal:
```bash
cd frontend

# Install packages
npm install

# Run Vite dev server
npm run dev
```

* The client will be available at [http://localhost:5173](http://localhost:5173) and connects directly to `http://localhost:8000`.

---

## 📁 Repository Structure

```text
rag-app/
├── .github/
│   └── workflows/
│       └── deploy-backend-azure.yml # CI/CD deployment to Azure Container Apps
├── backend/                         # FastAPI backend service
│   ├── rag_pipeline/                # RAG core modules
│   │   ├── documents/               # Source PDF regulation documents
│   │   ├── prompts/                 # Prompt versioning (v1.txt, v2.txt)
│   │   ├── chroma_db/               # Persistent Chroma vectorstore (generated at build, gitignored)
│   │   ├── bm25_retriever.pkl       # Pre-cached BM25 index (generated at build, gitignored)
│   │   ├── chunking.py              # Recursive character splitting logic
│   │   ├── vectorstore.py           # FastEmbed + ChromaDB setup
│   │   ├── retriever.py             # Hybrid ensemble (Dense MMR + Sparse BM25)
│   │   └── llm.py                   # OpenAI Responses API & SSE streaming
│   ├── Dockerfile                   # Production Dockerfile
│   ├── main.py                      # FastAPI server entry point
│   ├── routes.py                    # REST & SSE streaming endpoints (/ask)
│   ├── models.py                    # Pydantic request/response schemas
│   ├── rebuild_db.py                # Offline vectorstore & BM25 builder
│   └── requirements.txt             # Python dependencies
├── frontend/                        # React (Vite) client application
│   ├── src/
│   │   ├── components/              # ChatMessage, Header, ChunksPanel, WelcomeCard
│   │   ├── constants/               # Suggested regulatory questions
│   │   ├── App.jsx                  # State orchestrator & SSE consumer
│   │   └── App.css                  # Modern UI styles, telemetry popovers & animations
│   └── package.json                 # Node.js dependencies
├── docker-compose.yml               # Multi-container orchestration (backend + frontend)
└── README.md
```

---

## 👨‍💻 Author

**Dylan Estrada**  
💼 [LinkedIn](https://www.linkedin.com/in/dylan-estrada-606691216/) · 🐙 [GitHub](https://github.com/DylanEstrada9838)

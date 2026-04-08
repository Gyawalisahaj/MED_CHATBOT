# 🏥 Medical RAG Chatbot - System Architecture & Data Flow

## System Architecture Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MEDICAL RAG CHATBOT                                │
│                        Complete System Architecture                         │
└─────────────────────────────────────────────────────────────────────────────┘

                            FRONTEND LAYER (Streamlit)
                    ┌──────────────────────────────────────┐
                    │  Streamlit Chat Interface (8501)     │
                    │  ├─ Chat Messages Display            │
                    │  ├─ User Input Component             │
                    │  ├─ Source Citation Viewer           │
                    │  ├─ Chat History                     │
                    │  └─ Session Management               │
                    └──────────────────────────────────────┘
                                  ↓
                        (HTTP/REST API Calls)
                                  ↓
                    ┌──────────────────────────────────────┐
                    │      API GATEWAY (FastAPI 8001)      │
                    │  ├─ CORS Middleware                  │
                    │  ├─ Request Validation               │
                    │  └─ Response Formatting              │
                    └──────────────────────────────────────┘
                                  ↓
                    ┌──────────────────────────────────────┐
                    │      BUSINESS LOGIC LAYER            │
                    │                                      │
                    │  ┌────────────────────────────────┐  │
                    │  │ Chat Router                    │  │
                    │  │ ├─ POST /query                 │  │
                    │  │ ├─ GET /history/{session_id}   │  │
                    │  │ ├─ DELETE /history/{session_id}│  │
                    │  │ └─ GET /health                 │  │
                    │  └────────────────────────────────┘  │
                    │                                      │
                    │  ┌────────────────────────────────┐  │
                    │  │ Chat Service                   │  │
                    │  │ ├─ Query Processing            │  │
                    │  │ ├─ Cache Management            │  │
                    │  │ ├─ RAG Chain Execution         │  │
                    │  │ ├─ Source Extraction           │  │
                    │  │ └─ History Persistence         │  │
                    │  └────────────────────────────────┘  │
                    └──────────────────────────────────────┘
                                  ↓
                    ┌──────────────────────────────────────┐
                    │      RAG PIPELINE LAYER              │
                    │                                      │
                    │  ┌────────────────────────────────┐  │
                    │  │ Vector Store (Custom)         │  │
                    │  │ ├─ Sentence Transformers       │  │
                    │  │ ├─ Numpy-based Similarity      │  │
                    │  │ ├─ JSON Persistence            │  │
                    │  │ └─ Auto Document Loading       │  │
                    │  └────────────────────────────────┘  │
                    │                                      │
                    │  ┌────────────────────────────────┐  │
                    │  │ RAG Chain (Direct Groq)       │  │
                    │  │ ├─ Context Formatting          │  │
                    │  │ ├─ Groq API Integration       │  │
                    │  │ ├─ Source Attribution          │  │
                    │  │ └─ Error Handling              │  │
                    │  └────────────────────────────────┘  │
                    └──────────────────────────────────────┘
                                  ↓
                    ┌──────────────────────────────────────┐
                    │      DATA PERSISTENCE LAYER          │
                    │                                      │
                    │  ┌────────────────────────────────┐  │
                    │  │ SQLite Database                │  │
                    │  │ ├─ Chat History Table          │  │
                    │  │ ├─ Session Management          │  │
                    │  │ └─ Analytics Support           │  │
                    │  └────────────────────────────────┘  │
                    │                                      │
                    │  ┌────────────────────────────────┐  │
                    │  │ Document Storage               │  │
                    │  │ ├─ PDF Files in Document/      │  │
                    │  │ ├─ Automatic Loading           │  │
                    │  │ └─ Metadata Extraction         │  │
                    │  └────────────────────────────────┘  │
                    └──────────────────────────────────────┘
```

## Data Flow Architecture

### 1. User Interaction Flow
```
User Query → Streamlit UI → FastAPI Backend → RAG Pipeline → Response → UI Display
```

### 2. RAG Pipeline Flow
```
Query → Cache Check → Vector Retrieval → Context Formatting → Groq LLM → Source Attribution → Response
```

### 3. Document Processing Flow
```
PDF Files → PyPDF Loader → Text Splitting → Sentence Transformers → Vector Store → Similarity Search
```

## Component Details

### Frontend (Streamlit)
- **Technology**: Streamlit framework
- **Port**: 8501
- **Features**:
  - Real-time chat interface
  - Session management
  - Source citation display
  - Backend health monitoring
  - Responsive design

### Backend (FastAPI)
- **Technology**: FastAPI framework
- **Port**: 8001
- **Features**:
  - RESTful API endpoints
  - Request validation with Pydantic
  - CORS middleware
  - Automatic API documentation

### Vector Store (Custom Implementation)
- **Technology**: Numpy + Sentence Transformers
- **Features**:
  - In-memory embeddings with JSON persistence
  - Cosine similarity search
  - Automatic document loading
  - Efficient storage and retrieval

### RAG Chain (Direct Groq Integration)
- **Technology**: Direct API calls to Groq
- **Features**:
  - Context-aware prompting
  - Source attribution
  - Error handling and fallbacks
  - Medical-specific formatting

### Database (SQLite)
- **Technology**: SQLAlchemy ORM
- **Features**:
  - Chat history persistence
  - Session tracking
  - Query analytics support

## Performance Characteristics

- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **Vector Search**: Cosine similarity with top-k retrieval
- **LLM**: Groq llama-3.3-70b-versatile (fast inference)
- **Caching**: In-memory query cache with TTL
- **Storage**: JSON-based vector persistence

## Security Considerations

- API key management via environment variables
- Input validation and sanitization
- Educational disclaimers in responses
- No personal medical advice generation
- Source transparency for accountability
        ┌─────────────────────────┼─────────────────────────┐
        ↓                         ↓                         ↓
  ┌───────────────┐      ┌──────────────────┐    ┌──────────────────┐
  │  SQL Database │      │ Cache Layer      │    │  RAG Chain       │
  │   (SQLite)    │      │ (Vector Cache)   │    │                  │
  │               │      │                  │    │ 1. Normalizer    │
  │ ChatHistory   │      │ Similarity Check │    │ 2. Retriever     │
  │ DocMetadata   │      │ (95% threshold)  │    │ 3. Formatter     │
  │ Embeddings    │      │                  │    │ 4. LLM (Groq)    │
  └───────────────┘      └──────────────────┘    │ 5. Parser        │
        ↓                       ↓                  └──────────────────┘
        │                       │                          ↓
        └───────────────┬───────┴──────────────────────────┘
                        ↓
        ┌───────────────────────────────────┐
        │   DATA & INFRASTRUCTURE LAYER      │
        │                                   │
        │  ┌─────────────────────────────┐  │
        │  │  Vector Database (VDMS)     │  │
        │  │  ├─ Collection: medical_*   │  │
        │  │  ├─ Embeddings: FAISS       │  │
        │  │  ├─ Distance: L2            │  │
        │  │  └─ Index: ~50k chunks      │  │
        │  └─────────────────────────────┘  │
        │                                   │
        │  ┌─────────────────────────────┐  │
        │  │  External APIs              │  │
        │  │  ├─ Groq (LLM)              │  │
        │  │  │  └─ llama-3.3-70b        │  │
        │  │  └─ HuggingFace (Embeddings)│  │
        │  │     └─ MiniLM-L6-v2         │  │
        │  └─────────────────────────────┘  │
        │                                   │
        │  ┌─────────────────────────────┐  │
        │  │  Document Ingestion         │  │
        │  │  ├─ PDF Loader              │  │
        │  │  ├─ Text Splitter           │  │
        │  │  ├─ Batch Processing        │  │
        │  │  └─ Metadata Storage        │  │
        │  └─────────────────────────────┘  │
        └───────────────────────────────────┘
                        ↓
        ┌───────────────────────────────────┐
        │   DOCKER INFRASTRUCTURE           │
        │                                   │
        │  ┌──────────────┐  ┌───────────┐ │
        │  │ Backend      │  │ Frontend  │ │
        │  │ (Python 3.11)│  │ (Node 18) │ │
        │  └──────────────┘  └───────────┘ │
        │                                   │
        │  ┌──────────────┐                │
        │  │ VDMS Service │                │
        │  │ (55555)      │                │
        │  └──────────────┘                │
        │                                   │
        │  Shared Network: medical_network │
        └───────────────────────────────────┘
```

## Query Processing Pipeline (Detailed)

```
┌──────────────────────────────────────────────────────────────────────┐
│                  USER SUBMITS MEDICAL QUERY                          │
│         "What are the symptoms of diabetes mellitus?"                │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 1: Request Reception & Validation                              │
│                                                                      │
│ ChatRequest {                                                        │
│   message: "What are the symptoms of diabetes mellitus?",          │
│   session_id: "user_123_session"                                    │
│ }                                                                    │
│                                                                      │
│ ✓ Pydantic validation                                               │
│ ✓ Length checks (1-2000 chars)                                      │
│ ✓ Session ID mapping                                                │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 2: Query Normalization                                         │
│                                                                      │
│ Original: "What are the symptoms of diabetes mellitus?"            │
│ ↓ (lowercase, strip whitespace)                                     │
│ Normalized: "what are the symptoms of diabetes mellitus?"          │
│                                                                      │
│ Purpose: Consistent cache key generation                            │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 3: Cache Lookup (FAST PATH)                                    │
│                                                                      │
│ Query Vector Store:                                                  │
│   similarity_search(normalized_query, k=1)                          │
│                                                                      │
│ If similarity_score ≤ 0.95 (L2 distance):  ← Cached answer found  │
│   ✓ RETURN IMMEDIATELY (< 100ms)                                    │
│   ├─ Cached Answer: "Diabetes symptoms include..."                 │
│   ├─ Sources: ["Cached Knowledge Base"]                            │
│   └─ (Skip all below steps)                                         │
│                                                                      │
│ If no match:  ← Continue to full RAG pipeline                       │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 4: Vector Retrieval (SEMANTIC SEARCH)                          │
│                                                                      │
│ Retriever = VDMS.as_retriever(                                      │
│   search_type="mmr",      ← Maximum Marginal Relevance              │
│   search_kwargs={         ← Retrieves diverse, non-redundant docs   │
│     "k": 7,               ← Return top-7 most relevant documents    │
│     "fetch_k": 14         ← Search top-14, then re-rank             │
│   }                                                                  │
│ )                                                                    │
│                                                                      │
│ Query Processing:                                                    │
│   1. Convert query to embeddings (HuggingFace)                      │
│   2. Search VDMS vector database (FAISS index)                      │
│   3. Re-rank by relevance (MMR algorithm)                           │
│   4. Return top-7 most relevant chunks                              │
│                                                                      │
│ Retrieved Documents:                                                 │
│   Doc 1: "Diabetes mellitus symptoms: polyuria, polydipsia..." 
│           (Source: Harrison's, Page 1234)                           │
│   Doc 2: "Pathophysiology of type 2 diabetes..."                    │
│           (Source: Guyton, Page 567)                                │
│   Doc 3-7: ... (similar medical context chunks)                     │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 5: Context Formatting                                          │
│                                                                      │
│ Format retrieved documents for LLM:                                 │
│                                                                      │
│ Formatted Context:                                                   │
│ "Diabetes mellitus symptoms: polyuria, polydipsia...                │
│                                                                      │
│  Pathophysiology of type 2 diabetes...                              │
│                                                                      │
│  ... (concatenated document chunks)"                                │
│                                                                      │
│ Purpose: Provide clean, ordered context to LLM                      │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 6: LLM Processing (Groq API)                                   │
│                                                                      │
│ Prompt Template:                                                     │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ SYSTEM:                                                        │  │
│ │ "You are a medical information assistant designed for         │  │
│ │  educational purposes only. Answer using ONLY the provided   │  │
│ │  medical context. Do NOT diagnose or prescribe. Always end    │  │
│ │  with a disclaimer."                                          │  │
│ │                                                               │  │
│ │ CONTEXT:                                                      │  │
│ │ [Formatted documents from Step 5]                            │  │
│ │                                                               │  │
│ │ USER QUESTION:                                               │  │
│ │ "What are the symptoms of diabetes mellitus?"                │  │
│ │                                                               │  │
│ │ MEDICAL ANSWER:                                              │  │
│ └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│ LLM Model: llama-3.3-70b-versatile                                  │
│ Temperature: 0.0 (deterministic, factual)                           │
│                                                                      │
│ Generated Answer:                                                    │
│ "Diabetes mellitus manifests with various symptoms depending on     │
│  the type and stage of the disease. Key symptoms include:           │
│  • Polyuria (excessive urination)                                  │
│  • Polydipsia (excessive thirst)                                   │
│  • Weight loss                                                      │
│  ...                                                                │
│                                                                      │
│  Disclaimer: This information is for educational purposes only      │
│  and does not replace professional medical advice."                │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 7: Source Attribution                                          │
│                                                                      │
│ Extract source metadata from retrieved documents:                   │
│                                                                      │
│ Sources = [                                                          │
│   "Harrison's (Page 1234)",                                         │
│   "Guyton (Page 567)",                                              │
│   "Kumar & Clark's (Page 890)",                                     │
│   ...                                                                │
│ ]                                                                    │
│                                                                      │
│ Purpose: Citation, credibility, further reading                     │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 8: Cache Storage (for future queries)                          │
│                                                                      │
│ save_to_cache(                                                       │
│   question: "what are the symptoms of diabetes mellitus?",         │
│   answer: "[Generated medical answer from Step 6]"                  │
│ )                                                                    │
│                                                                      │
│ Creates Document:                                                    │
│ {                                                                    │
│   page_content: "what are the symptoms of diabetes mellitus?",    │
│   metadata: {                                                       │
│     answer: "[Generated answer]"                                   │
│   }                                                                  │
│ }                                                                    │
│                                                                      │
│ Stores in VDMS for future cache hits                               │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 9: Database Persistence                                        │
│                                                                      │
│ Store in SQLite chat_history table:                                 │
│                                                                      │
│ INSERT INTO chat_history (                                          │
│   session_id,                                                       │
│   message,                                                          │
│   response,                                                         │
│   sources,                                                          │
│   timestamp                                                         │
│ ) VALUES (                                                          │
│   'user_123_session',                                               │
│   'What are the symptoms of diabetes mellitus?',                   │
│   '[Generated answer]',                                             │
│   'Harrison|Guyton|Kumar&Clark',                                   │
│   CURRENT_TIMESTAMP                                                 │
│ )                                                                    │
│                                                                      │
│ Purpose: History tracking, analytics, multi-session support        │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 10: Response Formatting & Return                               │
│                                                                      │
│ ChatResponse {                                                      │
│   answer: "[Generated medical answer]",                             │
│   sources: [                                                        │
│     "Harrison's (Page 1234)",                                      │
│     "Guyton (Page 567)",                                           │
│     "Kumar & Clark's (Page 890)"                                   │
│   ],                                                                │
│   session_id: "user_123_session"                                    │
│ }                                                                    │
│                                                                      │
│ ✓ JSON serialized                                                   │
│ ✓ HTTP 200 response                                                 │
│ ✓ ~2-5 seconds total (including API latency)                        │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ FRONTEND DISPLAY                                                     │
│                                                                      │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ Assistant:                                                     │  │
│ │                                                                │  │
│ │ Diabetes mellitus manifests with various symptoms...          │  │
│ │ • Polyuria (excessive urination)                             │  │
│ │ • Polydipsia (excessive thirst)                              │  │
│ │ ...                                                            │  │
│ │                                                                │  │
│ │ Disclaimer: This information is for educational purposes...  │  │
│ │                                                                │  │
│ │ 📄 Sources [3 available]                                      │  │
│ │ ├─ Harrison's (Page 1234)                                    │  │
│ │ ├─ Guyton (Page 567)                                         │  │
│ │ └─ Kumar & Clark's (Page 890)                                │  │
│ └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│ Total Time: ~2-5 seconds (cached: < 100ms)                         │
└──────────────────────────────────────────────────────────────────────┘
```

## Module Responsibilities

```
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND MODULES & RESPONSIBILITIES              │
└─────────────────────────────────────────────────────────────────┘

app.main                          → FastAPI app initialization
│                                   - CORS setup
│                                   - Database initialization
│                                   - Router registration
│
├─ app.api.chat                   → HTTP endpoints
│  │                                 - POST /query
│  │                                 - GET /history/{session_id}
│  │                                 - DELETE /history/{session_id}
│  │                                 - GET /health
│  │
│  └─ app.services.chat_service   → Business logic
│     │                              - Query processing
│     │                              - Cache management
│     │                              - RAG chain execution
│     │                              - Source extraction
│     │                              - History persistence
│     │
│     ├─ app.rag.chain            → LangChain RAG chain
│     │  │                           - LCEL pipeline
│     │  │                           - Prompt templates
│     │  │                           - LLM integration
│     │  │
│     │  ├─ app.rag.retriever      → Vector retrieval
│     │  │  │                        - MMR search strategy
│     │  │  │                        - VDMS query execution
│     │  │  │
│     │  │  └─ app.rag.vectorstore → Vector database connection
│     │  │                           - VDMS client initialization
│     │  │                           - Collection management
│     │  │                           - Singleton pattern
│     │  │
│     │  └─ app.rag.embeddings     → Embedding model
│     │                              - HuggingFace embeddings
│     │                              - CPU/GPU support
│     │                              - Sentence-Transformers
│     │
│     ├─ app.rag.qa_cache          → Query caching
│     │  │                           - Similarity search
│     │  │                           - Cache storage
│     │  │                           - Metadata management
│     │  │
│     │  └─ [Uses: vectorstore]
│     │
│     └─ app.core.guardrails       → Safety checks
│                                    - Query validation
│                                    - Response verification
│                                    - Disclaimer injection
│
├─ app.db.session                  → Database configuration
│  │                                 - SQLAlchemy engine
│  │                                 - SessionLocal factory
│  │                                 - Base declarative
│  │
│  └─ app.models.history           → ORM models
│     │                              - ChatHistory table
│     │                              - DocumentMetadata table
│     │
│     └─ [Used by: chat_service]
│
├─ app.core.config                 → Configuration management
│  │                                 - Pydantic settings
│  │                                 - Environment variables
│  │                                 - Settings singleton
│  │
│  └─ [Used by: all services]
│
├─ app.core.prompts                → Prompt templates
│  │                                 - Medical RAG prompt
│  │                                 - Question condensation
│  │
│  └─ [Used by: rag.chain]
│
├─ app.schemas.chat                → Request/Response schemas
│  │                                 - ChatRequest
│  │                                 - ChatResponse
│  │                                 - ChatHistoryItem
│  │                                 - SearchRequest
│  │
│  └─ [Used by: api.chat]
│
└─ app.utils.logger                → Logging utility
                                     - Formatted logging
                                     - Log level management

┌─────────────────────────────────────────────────────────────────┐
│                  INGESTION PIPELINE                              │
└─────────────────────────────────────────────────────────────────┘

script.ingest_doc                  → Main ingestion orchestrator
│
├─ MedicalPDFIngester.load_pdfs()  → PDF loading
│  │                                 - Directory scanning
│  │                                 - PyPDF loader
│  │                                 - Metadata enrichment
│  │
│  └─ [Uses: app.rag.loader]
│
├─ MedicalPDFIngester.split_documents() → Document chunking
│  │                                      - Recursive splitting
│  │                                      - Medical optimization
│  │
│  └─ [Uses: app.rag.splitter]
│
├─ MedicalPDFIngester.ingest_to_vdms()  → Vector indexing
│  │                                      - VDMS connection
│  │                                      - Batch processing
│  │                                      - Embedding generation
│  │
│  └─ [Uses: app.rag.vectorstore]
│
└─ MedicalPDFIngester.save_metadata()   → Database storage
                                         - Document tracking
                                         - SQLite persistence

┌─────────────────────────────────────────────────────────────────┐
│                  FRONTEND MODULES (React)                        │
└─────────────────────────────────────────────────────────────────┘

App.js                            → Main application component
│
├─ Components/ChatMessage.js       → Message display
│  │                                - User messages
│  │                                - Assistant responses
│  │                                - Source display
│  │                                - Error handling
│  │
│  └─ [Renders: message content with styling]
│
├─ Components/ChatInput.js         → User input component
│  │                                - Text input field
│  │                                - Send button
│  │                                - Form submission
│  │
│  └─ [Handler: onSendMessage]
│
├─ Components/Sidebar.js           → Navigation sidebar
│  │                                - New chat button
│  │                                - Session display
│  │                                - History management
│  │                                - Quick links
│  │
│  └─ [Handlers: onNewChat, onClearHistory]
│
└─ styles/App.css                  → Global styling
                                    - Responsive design
                                    - Dark mode support
                                    - Animations
```

## Data Flow Between Components

```
┌──────────────────────────────────────────────────────────────┐
│                         DATA FLOW                             │
└──────────────────────────────────────────────────────────────┘

Frontend                          Backend                 External
─────────────────────────────────────────────────────────────────
React App
   │
   ├─ User Types Question
   │      ↓
   ├─ ChatInput captures input
   │      ↓
   ├─ axios.post('/api/v1/chat/query', {
   │      message: string,
   │      session_id: string
   │  })
   │         ├──────────────────→ API Endpoint (chat.py)
   │         │                        ├─ Validation (Pydantic)
   │         │                        ├─ Route to chat_service.py
   │         │                        │
   │         │                        ├─ Normalize query
   │         │                        ├─ Check cache
   │         │                        │      ├──→ VDMS (Cache lookup)
   │         │                        │      └─→ If hit: return
   │         │                        │
   │         │                        ├─ Retrieve documents
   │         │                        │      ├──→ VDMS (Vector search)
   │         │                        │      └─→ Get k=7 chunks
   │         │                        │
   │         │                        ├─ Call LLM
   │         │                        │      └──→ Groq API
   │         │                        │         (llama-3.3-70b)
   │         │                        │
   │         │                        ├─ Store in cache
   │         │                        │      └──→ VDMS (Add to cache)
   │         │                        │
   │         │                        ├─ Save to history
   │         │                        │      └──→ SQLite
   │         │                        │         (chat_history)
   │         │                        │
   │         │                        └─ Format response
   │         │
   │  ←──────┴─── ChatResponse {answer, sources, session_id}
   │
   ├─ Store in messages state
   │
   ├─ ChatMessage renders answer
   │      with source expander
   │
   └─ Display to user with styling

GET /api/v1/chat/history/{session_id}
   ├─→ API (chat.py)
   │   └─→ Query SQLite
   │       (chat_history table)
   │
   ←─── Array of ChatHistoryItem objects
        │
        └─→ Reverse order and render

DELETE /api/v1/chat/history/{session_id}
   ├─→ API (chat.py)
   │   └─→ Delete from SQLite
   │
   ←─── Success confirmation
        │
        └─→ Clear messages state
```

## Technology Stack Summary

```
┌──────────────────────────────────────────────────────────────┐
│ TECHNOLOGY STACK                                             │
└──────────────────────────────────────────────────────────────┘

BACKEND
├─ FastAPI                    → Web framework
├─ Uvicorn                    → ASGI server
├─ SQLAlchemy                 → ORM
├─ SQLite                     → Relational database
├─ LangChain                  → RAG orchestration
├─ LangChain-Groq             → LLM integration
├─ LangChain-HuggingFace      → Embeddings
├─ PyPDF                      → PDF loading
├─ Sentence-Transformers      → Embedding model
├─ VDMS Client                → Vector database
└─ Pydantic                   → Data validation

FRONTEND
├─ React 18                   → UI framework
├─ Axios                      → HTTP client
├─ UUID                       → Session management
├─ React Markdown             → Content rendering
├─ CSS3                       → Styling (Responsive)
└─ React Hooks                → State management

INFRASTRUCTURE
├─ Docker                     → Containerization
├─ Docker Compose             → Orchestration
├─ Python 3.11                → Backend runtime
├─ Node.js 18                 → Frontend runtime
└─ VDMS                       → Vector database service

EXTERNAL APIS
├─ Groq                       → LLM provider
│  └─ llama-3.3-70b-versatile
└─ HuggingFace                → Embedding models
   └─ sentence-transformers/all-MiniLM-L6-v2
```

## Error Handling Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  ERROR HANDLING FLOW                          │
└──────────────────────────────────────────────────────────────┘

User Query
    ↓
Try RAG Pipeline
    ├─ Success → Return ChatResponse ✓
    │
    └─ Exception Caught
        │
        ├─ Log error (logger.exception)
        │
        ├─ Save error state to database
        │
        └─ Return ChatResponse {
             answer: "Sorry, I couldn't process your query...",
             sources: ["System Error"],
             session_id: session_id
           }

Specific Error Cases:

1. Invalid Input
   → Pydantic validation error
   → HTTP 422 Unprocessable Entity

2. VDMS Connection Fails
   → Log error
   → Gracefully degrade (no cache)
   → Continue to retrieval

3. Groq API Unavailable
   → Catch exception
   → Return error message
   → Log for monitoring

4. Database Error
   → Log error
   → Don't crash application
   → Continue without persistence

5. Vector Search Returns Nothing
   → Use retrieved empty docs
   → LLM generates from context awareness
   → Return with low confidence
```

---

This comprehensive documentation serves as a reference for understanding the Medical RAG Chatbot architecture, data flow, and component interactions.

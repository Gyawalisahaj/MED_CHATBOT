# 🩺 MediQuery AI — Medical RAG Chatbot

An AI chatbot that answers medical questions using your own PDF textbooks.  
Ask anything → it searches the books → answers with citations.

> ⚠️ **Educational use only.** Not a substitute for professional medical advice.

---

## 📸 Preview

![Chat UI](screenshot/chat_ui.png)
*Main chat interface — type a medical question and get sourced answers*

![Chat Response](screenshot/chat_response.png)
*Answers with citations from books like Harrison's, Guyton, Kumar & Clark's*

![Chat Source](screenshot/chat_source.png)
![Chat Source](screenshot/chat_source2.png)
*Main chat interface — type a medical question and get sourced answers*
---

## 🤔 What / Why / How

| | |
|---|---|
| **What** | A chatbot that reads medical PDFs and answers questions from them |
| **Why** | Study smarter — get answers with page citations instead of Googling |
| **How** | Your question → vector search in book chunks → Groq LLM generates answer |

**Stack:** FastAPI (backend) · Next.js (frontend) · Sentence Transformers (search) · Groq Llama 3.3-70b (LLM) · SQLite/PostgreSQL (DBs)

---

## 📁 File Structure

```
chatbot/
├── backend/               # FastAPI REST API
│   ├── app/
│   │   ├── api/           # Routes (chat, auth)
│   │   ├── core/          # Config & security settings
│   │   ├── db/            # SQLite (history) & PostgreSQL (auth)
│   │   ├── models/        # DB models
│   │   ├── rag/           # RAG pipeline (embeddings, vector store, LLM chain)
│   │   ├── schemas/       # Pydantic request/response models
│   │   ├── services/      # Business logic (chat, auth)
│   │   └── main.py        # App entry point
│   └── vector_store/      # Saved vector index (auto-generated)
│
├── frontend/              # Next.js Chat UI
│   ├── src/
│   │   ├── app/           # Next.js Pages (login, register, chat)
│   │   ├── component/     # React Components (chat, ui)
│   │   ├── context/       # Auth & Conversation State
│   │   └── lib/           # API handlers
│
├── docker/                # Docker setup
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── script/
│   └── ingest_doc.py      # Load PDFs into vector store
│
├── Document/              # ← Put your medical PDFs here
├── backend/.env           # Backend config
├── frontend/.env          # Frontend config
└── requirements.txt
```

---

## 🚀 How to Start Locally

### 1. Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL (for user authentication)

### 2. Configure Environment Variables

Edit `backend/.env` with your settings:
```bash
GROQ_API_KEY=your_key_here
POSTGRES_URL=postgresql+psycopg2://user:password@localhost:5432/medchatbot
```

### 3. Add Medical PDFs & Ingest

Drop PDFs into the `Document/` folder, then run:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python ../script/ingest_doc.py
```

### 4. Start the Backend

```bash
cd backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Start the Frontend

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

### 6. Open in Browser

- 💬 **Chat UI:** http://localhost:3000
- 📖 **API Docs:** http://localhost:8000/docs

---

## 🐳 Docker (Alternative)

To run the full stack via Docker without manually installing Node.js/Python:

```bash
docker-compose -f docker/docker-compose.yml up -d --build
```
This starts the backend on port `8000` and the frontend on port `3000`.

---

## 🛠 Troubleshooting

**Vector store index empty?**
Ensure you have PDFs in the `Document` folder and have run the ingestion script. The app also attempts to auto-load documents on startup if the vector store is empty.

**Cannot log in or register?**
Check that your PostgreSQL database is running and the credentials match the `POSTGRES_URL` in `backend/.env`.

**No response from Chat?**
Ensure `GROQ_API_KEY` is properly set and you have internet access for the API.

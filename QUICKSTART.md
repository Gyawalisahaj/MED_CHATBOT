# ⚡ Quick Start Guide - Medical RAG Chatbot

**Time Required**: 10-15 minutes ⏱️

## 1️⃣ Prerequisites Check

```bash
# Check Docker
docker --version
docker-compose --version

# Should see: Docker version 20.x+ and Docker Compose version 2.x+
```

**Get Groq API Key**:
1. Visit https://console.groq.com/
2. Sign up (free account)
3. Generate API key from settings
4. Copy the key (you'll need it)

## 2️⃣ Clone & Configure (2 minutes)

```bash
# Navigate to project
cd chatbot

# Create environment file
cp .env.example .env

# Edit .env and add your Groq API key
# On Windows: notepad .env
# On macOS/Linux: nano .env

# Find this line and replace:
# GROQ_API_KEY=your_groq_api_key_here
```

## 3️⃣ Start Services (3 minutes)

```bash
# Build and start all containers
docker-compose -f docker/docker-compose.yml up -d --build

# Wait for services to start
# This may take 2-3 minutes on first run
```

**Verify services are running**:
```bash
docker-compose ps
# Should show: vdms, backend, frontend all as "running"
```

## 4️⃣ Ingest Medical PDFs (5 minutes)

```bash
# Wait ~30 seconds for VDMS to be fully ready
# Then run ingestion

docker-compose exec backend python script/ingest_doc.py

# You should see:
# ✅ INGESTION COMPLETED SUCCESSFULLY!
# 📊 Summary with chunk and batch counts
```

## 5️⃣ Access the Application

### Frontend (Streamlit)
```
http://localhost:8501
```

### Backend API (FastAPI)
```
http://localhost:8000
```

### API Documentation
```
http://localhost:8000/docs
```

## 6️⃣ Test It Out! 🎯

1. Open http://localhost:8501 in your browser
2. Type a medical question:
   - "What are the symptoms of diabetes?"
   - "Explain hypertension"
   - "How is pneumonia treated?"
3. Hit Enter and wait for the answer
4. Click "📄 Sources" to see citations

## 🎉 You're Done!

The chatbot is now running and ready to answer medical questions!

---

## 📱 Using the Interface

### Ask Questions
- Type any medical question in the input box
- Streamlit will send to backend, get answer from LLM
- Sources are automatically displayed

### Manage Sessions
- Each session is unique (UUID in sidebar)
- Click "🆕 New Chat" to start fresh
- Click "🗑️ Clear History" to delete conversation

### Monitor Status
- Green ✅ = Backend is online
- Red ❌ = Backend is offline (check logs)

### Change Backend URL
- If backend is on different machine
- Use "Backend URL" setting in sidebar
- Default: `http://localhost:8000`

---

## 🔧 Troubleshooting

### Services Not Starting?
```bash
# Check logs
docker-compose logs

# Rebuild everything
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### No PDFs Indexed?
```bash
# Check PDFs exist
ls Document/

# Run ingestion again
docker-compose exec backend python script/ingest_doc.py

# Check database
docker-compose exec backend sqlite3 medical_chatbot.db \
  "SELECT * FROM document_metadata;"
```

### "Cannot Connect to Backend"?
```bash
# Check backend is running
docker-compose ps backend

# Check logs
docker-compose logs backend

# Verify VDMS is online
docker-compose ps vdms
```

### Groq API Key Error?
```bash
# Check .env file
cat .env | grep GROQ_API_KEY

# Should not be empty. Get key from:
# https://console.groq.com/
```

---

## 📊 Expected Performance

| Operation | Time |
|-----------|------|
| Start services | 2-3 min |
| Ingest PDFs | 3-5 min |
| First query | 3-5 sec |
| Cache hit | <1 sec |

---

## 🧹 Cleanup (When Done)

```bash
# Stop all services
docker-compose down

# Remove database (if needed)
rm medical_chatbot.db

# Remove VDMS data (if needed)
docker volume rm chatbot_vdms_data
```

---

## 📚 Next Steps

### Learn More
- Read [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [GIT_COMMITS.md](GIT_COMMITS.md) for git strategy

### Customize
- Add more PDFs to `Document/` folder
- Re-run ingestion to index them
- Modify prompts in `backend/app/core/prompts.py`
- Adjust settings in `.env`

### Extend
- Add authentication
- Create mobile app
- Add voice features
- Build analytics dashboard

---

## ⚠️ Remember

- ✅ This is for **educational purposes only**
- ✅ Always consult real medical professionals
- ✅ Sources are provided for verification
- ✅ Keep your Groq API key secret
- ✅ Don't commit `.env` to git

---

## 🚀 That's It!

You now have a fully functional Medical RAG Chatbot running locally in Docker!

**Questions?** Check the docs or review service logs:
```bash
docker-compose logs -f backend
```

**Happy learning!** 🏥🤖

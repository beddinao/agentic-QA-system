# *`agentic-qa-system`*

*A chat system that reads your docs and answers questions with sources.*

## features

```
  - Real-time streaming answers (word by word)
  - Saves conversations automatically
  - Add docs via URL and scrapes them
  - Dark theme with glass UI
  - Quick setup
```

## stack

`Backend:` `FastAPI + LangChain + Pinecone + Supabase + OpenRouter`<br/>
`Frontend:` `Next.js + React + TypeScript + Tailwind`

## setup

### 1. Get API keys

- Supabase: https://supabase.com (get URL + Service Role Key)
- Pinecone: https://pinecone.io (get API Key + Environment)
- OpenRouter: https://openrouter.ai (get API Key)

### 2. Backend

```bash
cd backend

# create .env file with your keys
SUPABASE_URL=your-url
SUPABASE_SERVICE_ROLE_KEY=your-key

PINECONE_API_KEY=your-key
PINECONE_ENVIRONMENT=your-env
PINECONE_INDEX_NAME=your-index

OPENROUTER_API_KEY=your-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
BACKEND_PORT=8000

# install and run
pip install -U -r requirements.txt
python main.py
```

or

```bash
# create the .env file with the required cridentials
# in the project root and run docker compose

docker compose up
```

Backend runs at http://localhost:8000

### 3. Frontend

```bash
cd frontend

# create .env.local with the backend url
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# install and run
npm install
npm run dev
```

Frontend runs at http://localhost:3000

## how to use

1. **`Add documents`**: Click Ingest button, paste a URL, click submit
2. **`Ask questions`**: Type in chat box and press Enter
3. **`Toggle streaming`**: Click "Streaming" button to turn on/off
4. **`Conversations save`**: Reload page, same conversation loads

## api endpoints

### *POST `/api/chat`*
ask a question (wait for full answer)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "conversation_id": "optional"
  }'
```

### *POST `/api/chat/stream`*
ask a question (streaming, word by word)

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "conversation_id": "optional"
  }'
```

### *GET `/api/chat/history/{conversation_id}`*
get all messages from a conversation

```bash
curl http://localhost:8000/api/chat/history/conversation-id-123
```

### *POST `/api/ingest`*
creates a background job that add a document

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "https://docs.example.com"
  }'
```

### *GET `/api/ingest/status/{job_id}`*
check job status

```bash
curl -X GET http://localhost:8000/api/ingest/status/job_id-1232
```

### *GET `/`*
get a summary of available endpoints

```bash
curl -X GET http://localhost:8000/
```

### *GET `/health`*
check backend status

```bash
curl -X GET http://localhost:8000/
```

## postgreSQL database tables

**`conversations`**: stores conversations (id, title, created_at) <br/>
**`message`**: stores all messages (conversation_id, role, content, citations, created_at) <br/>
**`ingestion_jobs`**: tracks document processing (source_url, status, created_at, completed_at, error_message) <br/>
**`document_chunks`**: stores scraped websites by chunks (id, ingesion_job_id, content, metadata, chunk_index, source_url, created_at) <br/>

## deploy

```
- push to GitHub
```

### backend (Railway, Render, etc)

```
  - set environment variables on hosting platform
  - run: pip install -r requirements.txt && python main.py
```

### brontend (Vercel, Netlify, etc)

```
  - set: `NEXT_PUBLIC_API_BASE_URL=your-backend-url`
  - seploy
```

## troubleshooting

***'i can't connect to backend'***
```
  - check backend is running: python main.py
  - check frontend .env.local has right URL
  - check port 8000 is not used by something else
```

***"i ask a question but get no answer'***
```
  - add a document first (click Ingest)
  - check your OpenRouter key works
  - check Pinecone has data
```

***'streaming doesn't work'***
```
  - check backend is running
  - try switching to non-streaming mode
  - check network logs in browser
```

***'frontend won't start'***
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

***'conversation disappeared'***
```
  - same tab = same conversation (normal)
  - new tab = new conversation (normal)
```

## notes

- conversations saved in Supabase (you control it)
- needs internet (for AI and vector search)
- one person per chat session
- streaming is default, toggle anytime


## `TODO:`
```
- add login (multiple users)
- conversation list on sidebar
- upload files (not just URLs)
- pick AI model at runtime
- show token usage
```

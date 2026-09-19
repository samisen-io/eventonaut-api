# Eventonaut API — backend and RAG engine for the Conference Assistant apps

FastAPI backend for **Conference Assistant** and **Conference Buddy**, two mobile apps that help
attendees navigate multi-day conferences: agendas and sessions, speakers and exhibitors, ticketing,
push notifications — and an AI layer that answers attendee questions from the conference's own
content rather than from a general-purpose model.

The interesting part of this repo is that AI layer: a per-conference retrieval pipeline built on
LangChain + Pinecone, with conversational memory, streaming answers and per-call token accounting.

## The AI design (what to look at first)

| Concern | How it is handled | Where |
|---|---|---|
| Vector store | Pinecone, **one namespace per conference** — tenant isolation in the index rather than filtering at query time | `app/pinecone_operations.py` |
| Ingestion | Entities (events, sessions, speakers, exhibitors) → documents → embeddings, staged as CSV/JSON working files | `app/data_ingestion.py`, `app/file_type_handler.py` |
| Retrieval | `ConversationalRetrievalChain` over the conference namespace, OpenAI embeddings, explicit prompt template | `app/data_query.py` |
| Memory | Windowed conversation buffer in Redis/Upstash (`RedisChatMessageHistory`, `RunnableWithMessageHistory`) | `app/data_query.py` |
| Delivery | Token-by-token streaming responses to the mobile client (`StreamingResponse`) | `app/routers/ai_models.py` |
| Cost control | Every AI call is metered into an `aitokens` record via an OpenAI callback wrapper | `app/custom_manager.py`, `app/crud/aitokens_crud.py` |
| File handling | PDF/DOCX/CSV/XLSX loaders plus custom type handlers for conference exports | `app/file_type_handler.py`, `app/file_reader.py` |

Pipeline in one line: **conference content → documents → embeddings → Pinecone namespace → retrieval
with conversation memory → streamed grounded answer, metered per call.**

## Architecture

```
Conference Assistant / Conference Buddy (iOS, Android)
                │  REST
                ▼
        FastAPI routers (app/routers/*)
                │
        ┌───────┼──────────────┬───────────────┬──────────────┐
        ▼       ▼              ▼               ▼              ▼
   services   Postgres     Pinecone      Redis/Upstash   Azure Blob
 (ingestion,  (SQLAlchemy, (per-conf.    (chat memory)   (image upload)
  retrieval)   SQLModel)    namespace)
                │
                ▼
       OpenAI (chat + embeddings)
```

Other integrations in the same service: Razorpay for ticket checkout, OneSignal for push
notifications, an Eventbrite connector for importing events, OAuth2 with role-scoped access
(organizer vs attendee).

## API surface (selection)

- `PUT /create_vector_db` · `DELETE /delete_vector_db` — provision/drop a conference index
- `POST /query_the_document_stream/` — streamed RAG answer for a conference
- Session, speaker, exhibitor, attendee and conference CRUD routers
- `POST /assistant/create_assistant` and friends — configurable conference assistants
- Ticket checkout (Razorpay), image upload (Azure Blob), data visualization and agenda routers

## Configuration

Create a `.env` (variables below); nothing secret is committed to this repo — every credential is
read with `os.getenv`.

```ini
OPENAI_API_KEY=
SECRET_KEY=                       # access token signing
REFRESH_TOKEN_SECRET_KEY=
ALGORITHM=HS256
ORGANIZER_ACCESS_TOKEN_EXPIRE_MINUTES=60
ATTENDEE_ACCESS_TOKEN_EXPIRE_DAYS=10
DATABASE_URL_ADDRESS=postgresql://username:password@localhost:5432/database_name

PINECONE_API_KEY=
PINECONE_API_ENV=
PINECONE_API_INDEX=
UPSTASH_URL=                      # chat memory (or REDIS_HOST / REDIS_PORT / REDIS_PASSWORD)
UPSTASH_TOKEN=
AZURE_STORAGE_CONNECTION_STRING=  # image upload
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
EMAIL_ADDRESS=                    # OTP and notification mail
EMAIL_PASSWORD=
OTP_EXPIRE=300
CLIENT_ID=
CLIENT_SECRET=
```

## Run it

```bash
python3.10 -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt
# PostgreSQL running locally, .env populated
uvicorn app.main:app --reload        # http://localhost:8000
```

Container/deploy: `Dockerfile` (python:3.10-slim, libgl for OpenCV) and `Procfile`
(`uvicorn app.main:app --host 0.0.0.0 --port $PORT`). `restore_db.py` seeds a local database.

## Notes

- **Sample conference exports are deliberately not committed** (session, speaker and event files are
  third-party event data). The ingestion endpoints accept uploads and write their working files under
  `app/files/`, which is gitignored.
- Python 3.10 is the supported runtime; `opencv-python` is pulled in for image handling in uploads.
- `chromadb` is in `requirements.txt` from early experimentation; Pinecone is the canonical store in
  the code paths that ship.

## Limitations and next steps

- **No automated tests** — the clearest gap in this repo. The retrieval pipeline needs them most:
  golden question/answer pairs per conference, plus assertions that one tenant's namespace never
  leaks into another tenant's answers.
- No evaluation harness for answer quality or hallucination rate; answers are grounded by retrieval
  alone, with no scoring layer.
- Ingestion is synchronous per upload; large conference exports would benefit from a queue.
- Model and prompt are configurable but not versioned; prompt changes are not tracked as releases.

# Dental Clinic AI Receptionist

Voice AI receptionist built on LiveKit. Answers calls, collects appointment details (name, phone, date, time), books via n8n webhook. Supports English and Tamil.

## Live Demo

**[Try it here → https://abubasith86-appointment-agent.hf.space](https://abubasith86-appointment-agent.hf.space)**

```
Caller → LiveKit Room → STT → LLM (Agent) → TTS → Caller
                                  ↓
                            n8n Webhook → Clinic System
```

---

## Project Structure

```
voice/
├── livekit/                  Python LiveKit voice agent
│   ├── agent.py              Entry point — room connection, session setup
│   ├── config.py             All env var bindings + validation
│   ├── prompts/
│   │   └── dental_receptionist.txt   Agent system prompt
│   └── services/
│       ├── booking_service.py        Tool functions (book, get slots, datetime)
│       ├── llm_service.py            LLM provider factory
│       ├── stt_service.py            STT provider factory
│       ├── tts_service.py            TTS provider factory
│       └── prompt_service.py         Loads prompt by agent name
├── frontend/                 Vite + React UI
│   └── src/App.tsx           Language toggle + call interface
└── docker-compose.yml        Local dev
```

---

## Prerequisites

- [LiveKit Cloud](https://cloud.livekit.io) account (free tier works)
- API keys for your chosen STT / LLM / TTS providers
- n8n instance with two webhooks configured

---

## Local Development

### Agent

```bash
cd livekit
cp .env.example .env   # fill in your keys
uv sync
uv run python agent.py dev
```

### Frontend

```bash
cd frontend
cp .env.local.example .env.local   # fill in LiveKit credentials
npm install
npm run dev
```

Open `http://localhost:5173`, pick language, click **Start Call**.

---

## Environment Variables

### Agent — `livekit/.env`

| Variable | Required | Description |
|---|---|---|
| `LIVEKIT_URL` | Yes | `wss://your-project.livekit.cloud` |
| `LIVEKIT_API_KEY` | Yes | LiveKit API key |
| `LIVEKIT_API_SECRET` | Yes | LiveKit API secret |
| `N8N_WEBHOOK_URL` | Yes | POST endpoint to book appointment |
| `N8N_GET_TIMES_URL` | Yes | GET endpoint to fetch available slots |
| `LLM_PROVIDER` | Yes | `openai` / `anthropic` / `groq` / `google` / `ollama` |
| `STT_PROVIDER` | Yes | `deepgram` / `openai` / `google` / `azure` / `assemblyai` |
| `TTS_PROVIDER` | Yes | `elevenlabs` / `deepgram` / `openai` / `cartesia` |
| `OPENAI_API_KEY` | If using OpenAI LLM/STT/TTS | |
| `DEEPGRAM_API_KEY` | If using Deepgram STT/TTS | |
| `ELEVEN_API_KEY` | If using ElevenLabs TTS | |
| `ELEVEN_MODEL_ID` | No | Default: `eleven_turbo_v2_5` |
| `ELEVEN_VOICE_ID` | No | Default: Sarah (`EXAVITQu4vr4xnSDxMaL`) |
| `AGENT_NAME` | No | Prompt file to load. Default: `dental_receptionist` |
| `TOKEN_COUNTER_DIR` | No | Directory for daily token counter file. Default: project root |

### Frontend — `frontend/.env.local`

| Variable | Description |
|---|---|
| `VITE_LIVEKIT_URL` | Same as agent `LIVEKIT_URL` |
| `VITE_LIVEKIT_API_KEY` | Same as agent `LIVEKIT_API_KEY` |
| `VITE_LIVEKIT_API_SECRET` | Same as agent `LIVEKIT_API_SECRET` |

---

## Adding a New Agent

1. Create `livekit/prompts/<agent_name>.txt` with the system prompt
2. Set `AGENT_NAME=<agent_name>` in env
3. No code changes needed

---

## n8n Webhooks

| Webhook | Method | Payload |
|---|---|---|
| `N8N_WEBHOOK_URL` | POST | `{ name, phone, date, time, clinic }` |
| `N8N_GET_TIMES_URL` | GET | Returns `[{ Day, Time, Available }]` |

`get-appointment-times` response example:
```json
[
  { "Day": "Monday", "Time": "9:00 AM", "Available": "Yes" },
  { "Day": "Monday", "Time": "11:00 AM", "Available": "No" }
]
```

---

## Token Numbers

Daily sequential counter — resets to 1 each day. Stored in `.token_counter.json` in `TOKEN_COUNTER_DIR`. Mount a persistent volume in Docker so it survives restarts.

---

## Docker

### Local

```bash
# copy and fill env files first
cp livekit/.env.example livekit/.env
# set VITE_* in shell or .env at root

docker compose up --build
```

Frontend → `http://localhost:3000`

### Production (Coolify)

Deploy two separate services from the same repo:

**Agent service**
- Dockerfile: `livekit/Dockerfile`
- All agent env vars → Environment Variables in Coolify
- Add persistent volume: `/app/data`

**Frontend service**
- Dockerfile: `frontend/Dockerfile`
- Set `VITE_LIVEKIT_URL`, `VITE_LIVEKIT_API_KEY`, `VITE_LIVEKIT_API_SECRET` as **Build Variables**
- Port: `80`

> **Security:** `VITE_LIVEKIT_API_SECRET` is embedded in the browser bundle at build time. Acceptable for internal/demo use. For public production, move token generation to a server-side API route.

---

## Provider Reference

### LLM

| `LLM_PROVIDER` | Key var | Default model |
|---|---|---|
| `openai` | `OPENAI_API_KEY` | `gpt-4o-mini` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-3-5-sonnet-latest` |
| `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| `google` | `GEMINI_API_KEY` | `gemini-1.5-flash` |
| `ollama` | — | `llama3` |

### STT

| `STT_PROVIDER` | Key var | Notes |
|---|---|---|
| `deepgram` | `DEEPGRAM_API_KEY` | `nova-3`, multilingual (`language=multi`) |
| `openai` | `OPENAI_API_KEY` | Whisper |
| `assemblyai` | `ASSEMBLYAI_API_KEY` | |
| `azure` | `AZURE_STT_KEY` + `AZURE_STT_REGION` | |

### TTS

| `TTS_PROVIDER` | Key var | Notes |
|---|---|---|
| `elevenlabs` | `ELEVEN_API_KEY` | `eleven_turbo_v2_5` supports Tamil+English |
| `deepgram` | `DEEPGRAM_API_KEY` | |
| `openai` | `OPENAI_API_KEY` | |
| `cartesia` | `CARTESIA_API_KEY` | |

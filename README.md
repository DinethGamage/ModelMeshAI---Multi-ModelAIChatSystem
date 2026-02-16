# Multi-Model AI Chat System with Intelligent Routing + RAG

A production-grade AI chat system that intelligently routes queries to specialized models and supports document-based Q&A through RAG (Retrieval-Augmented Generation).

## 🌟 Features

- **🧠 Intelligent Routing**: Hybrid rule-based + LLM classification for optimal model selection
- **🔄 Multi-Turn Conversations**: Stateful sessions with conversation history
- **📄 RAG Pipeline**: Upload PDFs and query them with semantic search
- **🧮 Tool Integration**: Calculator tool for precise mathematical operations
- **🎯 Specialized Models**: Google Gemini Flash models (free tier)
- **💻 Modern React UI**: Beautiful, responsive chat interface
- **🐳 Docker Ready**: Full containerization support
- **📊 Routing Metadata**: Transparent routing decisions in API responses

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         FastAPI                             │
│                    (main.py)                                │
└───────────────┬─────────────────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Session Manager     │
    │   (session.py)        │
    └───────────┬───────────┘
                │
    ┌───────────┴───────────────────────┐
    │    Intelligent Router             │
    │    (router.py)                    │
    │  • Rule-based detection           │
    │  • LLM classification             │
    └───┬───────────────────────────────┘
        │
        ├─────────┬─────────┬─────────┬────────┐
        │         │         │         │        │
    ┌───▼──┐  ┌──▼──┐  ┌──▼───┐  ┌──▼──┐  ┌─▼───┐
    │Math  │  │Code │  │Gen.  │  │Doc  │  │RAG  │
    │Agent │  │Model│  │Model │  │Model│  │     │
    └──────┘  └─────┘  └──────┘  └─────┘  └─────┘
```

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `main.py` | FastAPI endpoints, request handling |
| `router.py` | Query classification and model routing |
| `models.py` | LLM initialization and management |
| `session.py` | Conversation history and state |
| `agents.py` | Calculator tool and math agent |
| `rag.py` | PDF processing and vector search |
| `config.py` | Configuration and environment variables |

## 📋 Requirements

- Python 3.11+
- Node.js 18+ (for React UI)
- Google Gemini API key (free tier supported)
- 4GB+ RAM (for embeddings)
- Docker (optional)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Google API key
GOOGLE_API_KEY=your_actual_api_key_here
```
Backend

#### Option A: Direct Python (Recommended)
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Docker
```bash
# Build and run with docker-compose
docker-compose up --build

# Or with docker directly
docker build -t ai-chat-system .
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key ai-chat-system
```

### 4. Run the React Frontend

**In a new terminal:**

```bash
cd frontend
npm install
npm run dev
```

### 5. Access the Application

- **🎨 React UI**: http://localhost:3000 (Main Interface)
- **📡 API Base**: http://localhost:8000
- **📖 API Docs**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/health

## 🎨 React UI Features

The modern React frontend provides:

- **💬 Real-time Chat**: Smooth chat interface with typing indicators
- **📄 PDF Upload**: Drag-and-drop PDF upload for document Q&A
- **🎯 Routing Display**: See which model handled each response
- **📊 Metadata**: View confidence scores, calculations, and context usage
- **🔄 Session Management**: Create new sessions or continue existing ones
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **🎨 Beautiful UI**: Modern gradient design with smooth animations

### Using the React UI

1. **Chat**: Type your message and press Enter or click Send
2. **Upload PDF**: Click "Upload PDF", select your file, and upload
3. **Query Documents**: Ask questions about your uploaded PDF
4. **View Routing**: See routing metadata below each AI response
5. **New Session**: Click "New Session" to start fresh

## 📡 API Endpoints

### POST `/chat`

Send a message and get an intelligent response.

**Request:**
```json
{
  "message": "What is 45 * 67 + 123?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "The answer is 3,138.",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "routing_metadata": {
    "route_category": "math",
    "model_used": "math",
    "routing_reason": "Detected mathematical expressions",
    "routing_method": "rule-based",
    "confidence": 0.85,
    "calculator_used": true,
    "calculation": "45 * 67 + 123",
    "calculation_result": 3138
  }
}
```

### POST `/upload-pdf`

Upload a PDF for document-based Q&A.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@document.pdf" \
  -F "session_id=your-session-id"
```

**Response:**
```json
{
  "message": "PDF uploaded and processed successfully",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "chunks_stored": 42
}
```

### GET `/session/{session_id}/history`

Retrieve conversation history.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_uploaded": true,
  "document_name": "document.pdf",
  "message_count": 10,
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

### DELETE `/session/{session_id}`

Delete a session and cleanup resources.

## 🧪 Testing Examples

### Math Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate the square root of 144 times 3"
  }'
```

### Coding Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a Python function to calculate fibonacci numbers"
  }'
```

### Document Query
```bash
# First upload a PDF
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@research_paper.pdf"

# Then query it (use session_id from upload response)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main findings in the document?",
    "session_id": "your-session-id-here"
  }'
```

## 🎯 Routing Logic

### Rule-Based Detection

The system first attempts fast rule-based classification:

| Query Type | Triggers |
|------------|----------|
| **Math** | Numeric expressions, operators (+, -, *, /), math keywords |
| **Coding** | Code blocks (```), function/class keywords, programming terms |
| **Document** | "document", "pdf", "according to", "uploaded" keywords |
| **Writing** | "write", "compose", "draft", "essay" keywords |

### LLM Classification

If rules are ambiguous (confidence < 0.7), the system uses Gemini for classification with structured output.

### Model Selection

| Category | Model | Temperature | Use Case |
|----------|-------|-------------|----------|
| Math | gemini-1.5-flash | 0.1 | Calculations, equations |
| Coding | gemini-1.5-flash | 0.7 | Programming, algorithms |
| Writing | gemini-1.5-flash | 0.7 | Creative content |
| Document | gemini-1.5-flash (RAG) | 0.7 | PDF Q&A |
| General | gemini-1.5-flash | 0.7 | Conversation |

## 🔧 Configuration

Edit [app/config.py](app/config.py) to customize:

```python
# Model selection (Free tier - all Flash models)
GEMINI_MODEL_GENERAL = "gemini-1.5-flash"
GEMINI_MODEL_CODE = "gemini-1.5-flash"
GEMINI_MODEL_MATH = "gemini-1.5-flash"
GEMINI_MODEL_DOCUMENT = "gemini-1.5-flash"

# RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RETRIEVAL = 3

# Embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

## 📁 Project Structure

```
.
├── app/                     # Backend application
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application
│   ├── router.py            # Intelligent routing logic
│   ├── models.py            # LLM initialization
│   ├── session.py           # Session management
│   ├── agents.py            # Calculator tool & math agent
│   ├── rag.py               # RAG pipeline
│   └── config.py            # Configuration
├── frontend/                # React UI
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API integration
│   │   ├── App.jsx          # Root component
│   │   └── main.jsx         # Entry point
│   ├── package.json         # Frontend dependencies
│   └── vite.config.js       # Vite configuration
├── data/                    # Uploaded PDFs (created automatically)
├── vectorstore/             # ChromaDB storage (created automatically)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker orchestration
├── start.bat / start.sh    # Backend startup scripts
├── start-frontend.bat/sh   # Frontend startup scripts
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # Documentation
```

## 🛠️ Development

### efine detection rules in [router.py](app/router.py)
2. Add model configuration in [config.py](app/config.py)
3. Update routing logic in [router.py](app/router.py)
4. Handle in [main.py](app/main.py) `/chat` endpoint

### Adding New Tools

1. Create tool class in [agents.py](app/agents.py)
2. Integrate with appropriate agent
3. Update routing metadata

## 🔒 Security Considerations

- API keys stored in environment variables (never commit `.env`)
- PDF upload size limits configurable
- Safe mathematical expression evaluation (no arbitrary code execution)
- Input validation with Pydantic models
- Session isolation for documents

## 📊 Performance

- **Response Time**: ~1-3s (depending on model)
- **RAG Query**: ~2-4s (with retrieval)
- **PDF Processing**: ~5-15s for 50-page document
- **Memory**: ~2-4GB for typical workload

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not found"
```bash
# Ensure .env file exists with valid API key
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### ChromaDB issues
```bash
# Clear vector store and restart
rm -rf vectorstore/
```

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Please ensure:
- Type hints on all functions
- Docstrings for modules and classes
- Modular, single-responsibility design
- Tests for new features

## 📧 Support

For issues or questions:
1. Check existing issues
2. Create detailed bug report
3. Include logs and system info

---

**Built with ❤️ using FastAPI, LangChain, and Google Gemini**

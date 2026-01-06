# 🧠 RAG Chatbot

A powerful Retrieval-Augmented Generation (RAG) chatbot application that answers questions based on your documents using Google's Gemini AI and FAISS vector search.

## 📋 Overview

This RAG chatbot combines the power of semantic search with large language models to provide accurate, context-aware answers from your document collection. It uses FAISS for efficient vector similarity search and Google Gemini for generating intelligent responses.

## ✨ Features

- **Production-Grade API**: FastAPI backend with REST endpoints, proper error handling, and logging
- **Document-based Q&A**: Ask questions about your documents and get accurate answers
- **Semantic Search**: Uses FAISS vector database for efficient document retrieval
- **Context-Aware Responses**: Maintains conversation history for better context understanding
- **Docker Support**: Fully containerized with Docker and Docker Compose for easy deployment
- **Modern Web UI**: Beautiful Streamlit-based interface for easy interaction
- **Multiple Document Support**: Process and query multiple text documents simultaneously
- **Chunked Processing**: Intelligent text chunking with overlap for better context retrieval
- **Health Checks**: Built-in health monitoring endpoints
- **Session Management**: Support for multiple conversation sessions

## 🏗️ Architecture

```
User Query → Document Retriever (FAISS) → Relevant Context → Gemini LLM → Response
```

1. **Document Processing**: Text files are cleaned, chunked, and embedded using Sentence Transformers
2. **Vector Search**: FAISS index enables fast similarity search across document embeddings
3. **Context Retrieval**: Top-k most relevant document chunks are retrieved for each query
4. **Response Generation**: Gemini LLM generates answers based on retrieved context and conversation history

## 🛠️ Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **Streamlit**: Web application framework for UI
- **Google Gemini API**: Large language model for response generation
- **FAISS**: Facebook AI Similarity Search for vector database
- **Sentence Transformers**: Text embeddings using `all-MiniLM-L6-v2` model
- **Docker**: Containerization for deployment
- **Uvicorn**: ASGI server for FastAPI
- **Python**: Core programming language

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RAGChatApp-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

   Or set it directly in your environment:
   ```bash
   export GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Build the vector index** (if not already built)
   ```bash
   cd src
   python build_index.py
   ```

   This will:
   - Process all `.txt` files in the `data/` directory
   - Generate embeddings using Sentence Transformers
   - Create FAISS index and save it to `embeddings/` directory

## 🚀 Usage

### Option 1: Docker Deployment (Recommended)

1. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the services**
   - **FastAPI Backend**: `http://localhost:8000`
   - **API Documentation**: `http://localhost:8000/docs`
   - **Streamlit UI**: `http://localhost:8501` (if enabled)

4. **Run only the API service**
   ```bash
   docker-compose up rag-api
   ```

### Option 2: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```

2. **Set up environment variables**
   
   Create a `.env` file:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Build the vector index** (if not already built)
   ```bash
   cd src
   python build_index.py
   ```

4. **Run FastAPI backend**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Run Streamlit UI** (optional)
   ```bash
   streamlit run app/streamlit_app.py
   ```

### Using the API

#### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI or `http://localhost:8000/redoc` for ReDoc.

#### Example API Calls

**Chat Endpoint:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key points about Chartered Accountants?",
    "use_history": true,
    "session_id": "user-123"
  }'
```

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Clear Session:**
```bash
curl -X DELETE "http://localhost:8000/chat/session/user-123"
```

#### Python Client Example

```python
import requests

# Chat endpoint
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "query": "Tell me about startup funding strategies",
        "use_history": True,
        "session_id": "my-session"
    }
)
print(response.json()["response"])
```

### Example Questions

Based on the included documents (CA conservation and Startups), you can ask:
- "What are the key points about Chartered Accountants?"
- "Tell me about startup funding strategies"
- "What documents are needed for CA registration?"

## 📁 Project Structure

```
RAGChatApp-main/
│
├── api/
│   └── main.py              # FastAPI backend application
│
├── app/
│   ├── streamlit_app.py      # Streamlit web UI
│   ├── chatbot.py            # RAG chatbot implementation
│   ├── retriever.py          # Document retrieval using FAISS
│   └── utils.py              # Utility functions (chunking, cleaning)
│
├── src/
│   └── build_index.py        # Script to build FAISS index from documents
│
├── data/
│   ├── CA_conservation.txt   # Sample document 1
│   └── startup.txt           # Sample document 2
│
├── embeddings/
│   ├── faiss_index.bin       # FAISS vector index
│   ├── faiss_index.pkl       # Document metadata
│   └── doc_embeddings.npy    # Document embeddings (optional)
│
├── Dockerfile                # Docker configuration for API
├── Dockerfile.streamlit      # Docker configuration for Streamlit UI
├── docker-compose.yml        # Docker Compose orchestration
├── requirement.txt           # Python dependencies
└── README.md                # This file
```

## 📡 API Endpoints

### `GET /`
Root endpoint with API information.

### `GET /health`
Health check endpoint. Returns service status and chatbot initialization state.

**Response:**
```json
{
  "status": "ok",
  "chatbot_initialized": true,
  "message": "healthy"
}
```

### `POST /chat`
Main chat endpoint for querying the RAG chatbot.

**Request Body:**
```json
{
  "query": "Your question here",
  "use_history": true,
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Generated answer based on documents",
  "session_id": "optional-session-id"
}
```

### `DELETE /chat/session/{session_id}`
Clear conversation history for a specific session.

### `POST /chat/clear`
Clear the default chatbot conversation history.

## ⚙️ Configuration

### Adding Your Own Documents

1. Place your `.txt` files in the `data/` directory
2. Rebuild the index:
   ```bash
   cd src
   python build_index.py
   ```
3. Restart the API service (or rebuild Docker container)

### Customizing the Model

You can modify the embedding model in `app/retriever.py`:
```python
model_name: str = 'all-MiniLM-L6-v2'  # Change to your preferred model
```

### Adjusting Retrieval Parameters

In `app/retriever.py`, modify the `k` parameter to retrieve more/fewer documents:
```python
def get_context(self, query: str, k: int = 3):  # Change k value
```

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `PYTHONUNBUFFERED`: Set to `1` for better logging in Docker

### Docker Configuration

Modify `docker-compose.yml` to:
- Change port mappings
- Add volume mounts
- Configure environment variables
- Adjust resource limits

## 🔧 How It Works

1. **Indexing Phase** (`build_index.py`):
   - Loads text files from `data/` directory
   - Cleans and chunks documents into smaller pieces
   - Generates embeddings using Sentence Transformers
   - Creates FAISS index for fast similarity search

2. **Query Phase** (`chatbot.py` + `retriever.py`):
   - User submits a question
   - Query is embedded using the same model
   - FAISS searches for top-k similar document chunks
   - Retrieved context is formatted and sent to Gemini
   - Gemini generates response based on context and history

3. **Response Generation**:
   - Combines retrieved context with conversation history
   - Sends formatted prompt to Gemini API
   - Returns generated response to user

## 🐳 Docker Commands

### Build and Run
```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f rag-api

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build rag-api
```

### Individual Docker Commands
```bash
# Build image
docker build -t rag-chatbot-api .

# Run container
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key rag-chatbot-api

# Run with volume mounts
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/embeddings:/app/embeddings \
  -v $(pwd)/data:/app/data \
  rag-chatbot-api
```

## 📝 Notes

- The chatbot maintains conversation history for context-aware responses
- Document chunks are retrieved based on cosine similarity
- The app uses `gemini-2.5-flash` model by default
- Chat history can be cleared via API endpoints or Streamlit UI
- Session management supports multiple concurrent users
- Logs are written to `app.log` and console
- Health checks are available at `/health` endpoint
- API documentation is auto-generated at `/docs` (Swagger) and `/redoc` (ReDoc)

## 🔒 Production Considerations

For production deployment, consider:

1. **Security**:
   - Use environment variables for sensitive data
   - Implement API rate limiting
   - Add authentication/authorization
   - Configure CORS properly (not `allow_origins=["*"]`)

2. **Performance**:
   - Use Redis for session management instead of in-memory
   - Implement caching for frequent queries
   - Use production ASGI server (Gunicorn + Uvicorn workers)
   - Consider using FAISS-GPU for larger datasets

3. **Monitoring**:
   - Add structured logging
   - Integrate with monitoring tools (Prometheus, Grafana)
   - Set up alerting for health check failures

4. **Scalability**:
   - Use load balancer for multiple API instances
   - Consider message queue for async processing
   - Use distributed vector database for large-scale deployments

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Google Gemini for the LLM API
- Facebook AI Research for FAISS
- Sentence Transformers for embeddings
- FastAPI for the modern API framework
- Streamlit for the web framework
- Docker for containerization

---

**Happy Chatting! 🚀**


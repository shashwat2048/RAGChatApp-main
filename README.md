# 🧠 RAG Chatbot

A powerful Retrieval-Augmented Generation (RAG) chatbot application that answers questions based on your documents using Google's Gemini AI and FAISS vector search.

## 📋 Overview

This RAG chatbot combines the power of semantic search with large language models to provide accurate, context-aware answers from your document collection. It uses FAISS for efficient vector similarity search and Google Gemini for generating intelligent responses.

## ✨ Features

- **Document-based Q&A**: Ask questions about your documents and get accurate answers
- **Semantic Search**: Uses FAISS vector database for efficient document retrieval
- **Context-Aware Responses**: Maintains conversation history for better context understanding
- **Modern Web UI**: Beautiful Streamlit-based interface for easy interaction
- **Multiple Document Support**: Process and query multiple text documents simultaneously
- **Chunked Processing**: Intelligent text chunking with overlap for better context retrieval

## 🏗️ Architecture

```
User Query → Document Retriever (FAISS) → Relevant Context → Gemini LLM → Response
```

1. **Document Processing**: Text files are cleaned, chunked, and embedded using Sentence Transformers
2. **Vector Search**: FAISS index enables fast similarity search across document embeddings
3. **Context Retrieval**: Top-k most relevant document chunks are retrieved for each query
4. **Response Generation**: Gemini LLM generates answers based on retrieved context and conversation history

## 🛠️ Technologies Used

- **Streamlit**: Web application framework
- **Google Gemini API**: Large language model for response generation
- **FAISS**: Facebook AI Similarity Search for vector database
- **Sentence Transformers**: Text embeddings using `all-MiniLM-L6-v2` model
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

### Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run app/streamlit_app.py
   ```

2. **Access the web interface**
   - The app will open automatically in your browser
   - Or navigate to `http://localhost:8501`

3. **Using the Chatbot**
   - Enter your Gemini API key in the sidebar (if not set in `.env`)
   - Type your question in the chat input
   - Get answers based on your documents!

### Example Questions

Based on the included documents (CA conservation and Startups), you can ask:
- "What are the key points about Chartered Accountants?"
- "Tell me about startup funding strategies"
- "What documents are needed for CA registration?"

## 📁 Project Structure

```
RAGChatApp-main/
│
├── app/
│   ├── streamlit_app.py      # Main Streamlit web application
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
├── requirement.txt           # Python dependencies
└── README.md                # This file
```

## ⚙️ Configuration

### Adding Your Own Documents

1. Place your `.txt` files in the `data/` directory
2. Rebuild the index:
   ```bash
   cd src
   python build_index.py
   ```
3. Restart the Streamlit app

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

## 📝 Notes

- The chatbot maintains conversation history for context-aware responses
- Document chunks are retrieved based on cosine similarity
- The app uses `gemini-2.5-flash` model by default
- Chat history can be cleared using the sidebar button

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Google Gemini for the LLM API
- Facebook AI Research for FAISS
- Sentence Transformers for embeddings
- Streamlit for the web framework

---

**Happy Chatting! 🚀**


# 🚀 RAG Pipeline - Retrieval-Augmented Generation System

A production-ready RAG (Retrieval-Augmented Generation) system built with LangChain, featuring multiple embedding options, vector stores, and LLM integration.

## ✨ Features

- **🔍 Multiple Document Types**: Support for TXT, PDF, and web URLs
- **🧠 Dual Embedding Options**: HuggingFace (default) + Ollama fallback
- **🗄️ Vector Store Options**: FAISS and Chroma support
- **🔗 Complete RAG Chain**: Full retrieval-augmented generation pipeline
- **🌐 LLM Integration**: Groq, OpenAI, and other LangChain LLMs
- **📊 LangChain Tracking**: Built-in monitoring and tracing
- **⚡ Production Ready**: Error handling, logging, and configuration management

## 🏗️ Architecture

```
Documents → Text Splitting → Embeddings → Vector Store → Retrieval → LLM → Response
    ↓              ↓            ↓           ↓           ↓        ↓       ↓
TextLoader   RecursiveChar   HuggingFace  FAISS/Chroma  RAG     Groq   Final
PDFLoader    TextSplitter    Ollama       Vector DB     Chain   OpenAI  Answer
WebLoader
```

## 🚀 Quick Start

### 1. Virtual Environment Setup (Recommended)

```bash
# Navigate to the rag_pipeline folder
cd langchain/rag_pipeline

# Create virtual environment
python -m venv rag_env

# Activate virtual environment
# On Linux/Mac:
source rag_env/bin/activate
# On Windows:
# rag_env\Scripts\activate

# Verify activation (you should see (rag_env) in your prompt)
```

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the `rag_pipeline` folder:

```bash
# Required for LLM integration
GROQ_API_KEY=gsk_your_groq_api_key_here

# LangChain tracking (optional but recommended)
LANGSMITH_API_KEY=lsv2_your_langsmith_api_key_here
LANGCHAIN_PROJECT=YourProjectName
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# Alternative LLM options
OPENAI_API_KEY=sk_your_openai_api_key_here
ANTHROPIC_API_KEY=sk_ant_your_anthropic_api_key_here
```

### 3. Basic Usage

```python
from rag_implementation import RAGSystem

# Initialize RAG system (uses HuggingFace embeddings by default)
rag = RAGSystem()

# Load documents
documents = rag.load_documents(["speech.txt", "document.pdf", "https://example.com"])

# Create vector store
rag.create_vectorstore(documents, "faiss")

# Setup RAG chain with LLM
from langchain_groq import ChatGroq
llm = ChatGroq(groq_api_key="your_key", model_name="gemma2-9b-it")
rag.setup_rag_chain(llm)

# Query the system
response = rag.query("What is the main theme of this document?")
print(response)
```

## 📚 API Reference

### RAGSystem Class

#### Constructor
```python
RAGSystem(
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    use_ollama: bool = False
)
```

**Parameters:**
- `embedding_model`: HuggingFace model name or Ollama model
- `use_ollama`: Whether to use Ollama instead of HuggingFace

#### Methods

##### `load_documents(file_paths: List[str]) -> List`
Loads documents from various sources.

**Supported formats:**
- `.txt` files → `TextLoader`
- `.pdf` files → `PyPDFLoader`
- URLs → `WebBaseLoader`

##### `create_vectorstore(documents: List, vectorstore_type: str = "faiss")`
Creates a vector store from documents.

**Vector store types:**
- `"faiss"` → FAISS vector database
- `"chroma"` → Chroma vector database

##### `setup_rag_chain(llm, prompt_template: str = None)`
Sets up the RAG retrieval chain.

**Parameters:**
- `llm`: LangChain language model instance
- `prompt_template`: Custom prompt template (optional)

##### `query(question: str) -> str`
Queries the RAG system and returns an answer.

## 🔧 Configuration Options

### Embedding Models

#### HuggingFace Models (Default)
```python
# High-quality, pre-trained models
rag = RAGSystem(embedding_model="sentence-transformers/all-MiniLM-L6-v2")
rag = RAGSystem(embedding_model="sentence-transformers/all-mpnet-base-v2")
rag = RAGSystem(embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
```

#### Ollama Models (Local)
```python
# Local models - requires Ollama running
rag = RAGSystem(embedding_model="nomic-embed-text", use_ollama=True)
rag = RAGSystem(embedding_model="llama2", use_ollama=True)
```

### Vector Store Options

```python
# FAISS (recommended for production)
rag.create_vectorstore(documents, "faiss")

# Chroma (good for development)
rag.create_vectorstore(documents, "chroma")
```

### LLM Integration

```python
# Groq (fast, cost-effective)
from langchain_groq import ChatGroq
llm = ChatGroq(groq_api_key="your_key", model_name="gemma2-9b-it")

# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(openai_api_key="your_key", model="gpt-3.5-turbo")

# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(anthropic_api_key="your_key", model="claude-3-sonnet-20240229")
```

## 🧪 Testing

### Test Core Functionality
```bash
# Test embeddings and vector store (no API keys required)
python test_embeddings.py
```

### Test Full RAG System
```bash
# Test complete RAG pipeline (requires API keys)
python rag_implementation.py
```

## 📁 File Structure

```
rag_pipeline/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── rag_implementation.py     # Main RAG system
├── test_embeddings.py       # Testing script
├── speech.txt               # Sample document
└── .env                     # Environment variables (create this)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Virtual Environment Issues
```bash
# Create virtual environment
python -m venv rag_env

# Activate virtual environment
# On Linux/Mac:
source rag_env/bin/activate
# On Windows:
# rag_env\Scripts\activate

# Verify activation (should see (rag_env) in prompt)
# Then install requirements
pip install -r requirements.txt
```

#### 2. Import Errors
```bash
# Make sure virtual environment is activated
# Install missing packages
pip install -r requirements.txt
```

#### 2. Embedding Issues
```bash
# For HuggingFace issues
pip install sentence-transformers torch transformers

# For Ollama issues
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull nomic-embed-text
```

#### 3. API Key Errors
- Ensure your `.env` file is in the `rag_pipeline` folder
- Verify API keys are correct and have sufficient credits
- Check if the API service is available

#### 4. Memory Issues
- Use smaller embedding models
- Reduce chunk size in text splitting
- Use CPU-only PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

## 🔗 Useful Links

- **LangChain Documentation**: https://python.langchain.com/
- **Groq Console**: https://console.groq.com/
- **LangSmith**: https://smith.langchain.com/
- **HuggingFace Models**: https://huggingface.co/sentence-transformers
- **Ollama**: https://ollama.ai/

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this RAG pipeline!

---

**Happy RAG-ing! 🚀**

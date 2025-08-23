"""
Clean RAG Implementation for LangChain
This file provides a proper RAG (Retrieval-Augmented Generation) implementation
using the latest LangChain imports and best practices.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variable configuration
def load_environment():
    """Load and validate required environment variables."""
    required_vars = {
        "GROQ_API_KEY": "Required for Groq LLM integration"
    }
    
    # Check for LangChain API key (either LANGCHAIN_API_KEY or LANGSMITH_API_KEY)
    langchain_api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("Example .env file:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        print("LANGSMITH_API_KEY=your_langsmith_api_key_here")
        print("LANGCHAIN_PROJECT=YourProjectName")
        print("LANGCHAIN_TRACING_V2=true")
        print("LANGCHAIN_ENDPOINT=https://api.smith.langchain.com")
        print()
    
    # Set LangChain environment variables
    if langchain_api_key:
        os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        print("✅ LangChain tracking enabled")
        print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'Not set')}")
        print(f"   Endpoint: {os.getenv('LANGCHAIN_ENDPOINT', 'Not set')}")
    else:
        print("ℹ️  LangChain tracking disabled (LANGSMITH_API_KEY not set)")
    
    return len(missing_vars) == 0

# Load environment on import
env_loaded = load_environment()

# LangChain imports - using latest versions
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader, PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_groq import ChatGroq

class RAGSystem:
    """A clean RAG system implementation using LangChain."""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2", use_ollama: bool = False):
        """Initialize the RAG system.
        
        Args:
            embedding_model: The embedding model to use (HuggingFace model name or Ollama model)
            use_ollama: Whether to use Ollama embeddings (requires Ollama running)
        """
        self.use_ollama = use_ollama
        if use_ollama:
            try:
                self.embeddings = OllamaEmbeddings(model=embedding_model)
                print(f"✅ Using Ollama embeddings with model: {embedding_model}")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Ollama embeddings: {e}")
                print("   Please ensure Ollama is running: ollama serve")
                print("   Or set use_ollama=False to use HuggingFace embeddings")
                raise
        else:
            # Use HuggingFace embeddings by default
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                try:
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                except ImportError:
                    print("⚠️  HuggingFace embeddings not available. Please install: pip install langchain-huggingface")
                    raise
            
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=embedding_model,
                    model_kwargs={'device': 'cpu'}
                )
                print(f"✅ Using HuggingFace embeddings with model: {embedding_model}")
                print("   This model will be downloaded automatically on first use")
            except Exception as e:
                print(f"⚠️  Error initializing HuggingFace embeddings: {e}")
                raise
        
        self.vectorstore = None
        self.retrieval_chain = None
        
    def load_documents(self, file_paths: List[str]) -> List:
        """Load documents from various file types.
        
        Args:
            file_paths: List of file paths to load
            
        Returns:
            List of loaded documents
        """
        documents = []
        
        for file_path in file_paths:
            if file_path.endswith('.txt'):
                loader = TextLoader(file_path)
            elif file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.startswith('http'):
                loader = WebBaseLoader(file_path)
            else:
                print(f"Unsupported file type: {file_path}")
                continue
                
            try:
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded {len(docs)} documents from {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        return documents
    
    def create_vectorstore(self, documents: List, vectorstore_type: str = "faiss"):
        """Create a vector store from documents.
        
        Args:
            documents: List of documents to index
            vectorstore_type: Type of vector store ("faiss" or "chroma")
        """
        if not documents:
            raise ValueError("No documents provided")
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Create vector store
        if vectorstore_type.lower() == "faiss":
            self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        elif vectorstore_type.lower() == "chroma":
            self.vectorstore = Chroma.from_documents(split_docs, self.embeddings)
        else:
            raise ValueError("vectorstore_type must be 'faiss' or 'chroma'")
            
        print(f"Created {vectorstore_type.upper()} vector store with {len(split_docs)} chunks")
    
    def setup_rag_chain(self, llm, prompt_template: str = None):
        """Set up the RAG retrieval chain.
        
        Args:
            llm: The language model to use
            prompt_template: Custom prompt template (optional)
        """
        if not self.vectorstore:
            raise ValueError("Vector store not created. Call create_vectorstore() first.")
            
        # Default prompt template
        if not prompt_template:
            prompt_template = """Answer the question based on the provided context only.
            Please provide the most accurate response based on the question.
            
            Context: {context}
            
            Question: {input}
            
            Answer:"""
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Create document chain
        document_chain = create_stuff_documents_chain(llm, prompt)
        
        # Create retrieval chain
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        print("RAG chain setup complete")
    
    def query(self, question: str) -> str:
        """Query the RAG system.
        
        Args:
            question: The question to ask
            
        Returns:
            The answer based on retrieved context
        """
        if not self.retrieval_chain:
            raise ValueError("RAG chain not set up. Call setup_rag_chain() first.")
            
        try:
            response = self.retrieval_chain.invoke({"input": question})
            return response['answer']
        except Exception as e:
            return f"Error processing query: {e}"

def main():
    """Example usage of the RAG system."""
    
    # Check if environment is properly loaded
    if not env_loaded:
        print("❌ Environment not properly configured. Please check your .env file.")
        return
    
    # Initialize RAG system with HuggingFace embeddings by default
    try:
        print("🔄 Initializing RAG system with HuggingFace embeddings...")
        rag = RAGSystem(use_ollama=False)
    except Exception as e:
        print(f"❌ HuggingFace embeddings failed: {e}")
        print("\n🔄 Trying Ollama embeddings as fallback...")
        try:
            rag = RAGSystem(use_ollama=True)
        except Exception as e2:
            print(f"❌ Ollama embeddings also failed: {e2}")
            print("\n💡 To use HuggingFace embeddings:")
            print("   pip install sentence-transformers")
            print("\n💡 To use Ollama embeddings:")
            print("   1. Install Ollama: https://ollama.ai/")
            print("   2. Run: ollama serve")
            print("   3. Pull model: ollama pull nomic-embed-text")
            return
    
    # Load documents (example with speech.txt)
    documents = rag.load_documents(["speech.txt"])
    
    # Create vector store
    rag.create_vectorstore(documents, "faiss")
    
    # Initialize LLM (using Groq as in your other examples)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please add GROQ_API_KEY=your_key_here to your .env file")
        return
        
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="gemma2-9b-it",
        temperature=0.2
    )
    
    # Setup RAG chain
    rag.setup_rag_chain(llm)
    
    # Example queries
    questions = [
        "What is the main theme of this speech?",
        "Who is the speaker addressing?",
        "What does the speaker say about the future of their people?"
    ]
    
    print("\n" + "="*50)
    print("RAG SYSTEM DEMO")
    print("="*50)
    
    for question in questions:
        print(f"\nQuestion: {question}")
        answer = rag.query(question)
        print(f"Answer: {answer}")
        print("-" * 30)

if __name__ == "__main__":
    main()

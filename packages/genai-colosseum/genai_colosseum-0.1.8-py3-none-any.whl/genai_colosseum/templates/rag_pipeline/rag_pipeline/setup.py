#!/usr/bin/env python3
"""
RAG Pipeline Setup Script
This script helps you set up the RAG pipeline environment and test the installation.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print the setup header."""
    print("🚀 RAG Pipeline Setup")
    print("=" * 50)

def check_virtual_environment():
    """Check if running in a virtual environment."""
    print("🔍 Checking virtual environment...")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return True
    else:
        print("⚠️  No virtual environment detected")
        print("   It's recommended to use a virtual environment to avoid conflicts")
        print("   Create one with: python -m venv rag_env")
        print("   Activate with: source rag_env/bin/activate (Linux/Mac) or rag_env\\Scripts\\activate (Windows)")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages."""
    print("\n📦 Installing required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file from template."""
    print("\n🔧 Setting up environment file...")
    
    env_file = Path(".env")
    template_file = Path("env_template.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not template_file.exists():
        print("❌ env_template.txt not found")
        return False
    
    try:
        # Copy template to .env
        with open(template_file, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created from template")
        print("   Please edit .env and add your API keys")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_imports():
    """Test if all required packages can be imported."""
    print("\n🧪 Testing imports...")
    
    try:
        import langchain_core
        import langchain_community
        import langchain_text_splitters
        import langchain_huggingface
        import langchain_groq
        import sentence_transformers
        import faiss
        print("✅ All core packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def run_basic_test():
    """Run basic functionality test."""
    print("\n🧪 Running basic functionality test...")
    
    try:
        result = subprocess.run([sys.executable, "test_embeddings.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Basic functionality test passed")
            return True
        else:
            print(f"❌ Basic functionality test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("=" * 50)
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - GROQ_API_KEY (recommended)")
    print("   - LANGSMITH_API_KEY (optional)")
    print("\n2. Test the system:")
    print("   python test_embeddings.py")
    print("\n3. Run the full RAG implementation:")
    print("   python rag_implementation.py")
    print("\n4. Read the README.md for detailed usage")
    print("\n🔗 Useful Links:")
    print("   - Groq Console: https://console.groq.com/")
    print("   - LangSmith: https://smith.langchain.com/")
    print("   - Documentation: README.md")

def main():
    """Main setup function."""
    print_header()
    
    # Check virtual environment
    check_virtual_environment()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("\n⚠️  Could not create .env file. Please create it manually.")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check your installation.")
        sys.exit(1)
    
    # Run basic test
    if not run_basic_test():
        print("\n⚠️  Basic test failed. You may need to configure your .env file first.")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()

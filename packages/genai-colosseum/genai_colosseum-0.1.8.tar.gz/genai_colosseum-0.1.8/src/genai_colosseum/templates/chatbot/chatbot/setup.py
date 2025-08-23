#!/usr/bin/env python3
"""
Simple Chatbot Setup Script
Quick setup for the chatbot application
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print the setup header."""
    print("🤖 Chatbot Setup")
    print("=" * 30)

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_virtual_environment():
    """Check if running in a virtual environment."""
    print("🔍 Checking virtual environment...")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return True
    else:
        print("⚠️  No virtual environment detected")
        print("   Recommended: python -m venv chatbot_env")
        print("   Then: source chatbot_env/bin/activate")
        return False

def install_requirements():
    """Install required packages."""
    print("\n📦 Installing requirements...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    print("\n🔧 Setting up environment file...")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    # Create simple .env file
    env_content = """# Chatbot Environment Variables
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional: LangChain tracking
LANGSMITH_API_KEY=lsv2_your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created")
        print("   Please edit it and add your GROQ_API_KEY")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_imports():
    """Test if all required packages can be imported."""
    print("\n🧪 Testing imports...")
    
    try:
        import langchain_core
        import langchain_groq
        import streamlit
        print("✅ All packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 30)
    print("🎉 Setup Complete!")
    print("=" * 30)
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your GROQ_API_KEY")
    print("2. Run the chatbot: streamlit run app.py")
    print("3. Open your browser to the displayed URL")
    print("\n🔗 Get API Key: https://console.groq.com/")

def main():
    """Main setup function."""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check virtual environment
    check_virtual_environment()
    
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
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()

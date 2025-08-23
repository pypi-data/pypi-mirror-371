# 🤖 Simple Chatbot

A clean, simple chatbot built with LangChain and Groq, featuring a Streamlit web interface.

## ✨ Features

- **🧠 Groq LLM Integration** - Fast and cost-effective
- **🌐 Streamlit Web Interface** - Easy to use
- **🔧 Simple Configuration** - Just add your API key
- **📱 Responsive Design** - Works on all devices

## 🚀 Quick Start

### 1. 🐍 Setup Virtual Environment
```bash
cd langchain/chatbot

# Create virtual environment
python -m venv chatbot_env

# Activate (Linux/Mac)
source chatbot_env/bin/activate
# Activate (Windows)
# chatbot_env\Scripts\activate
```

### 2. 📦 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. 🔑 Add API Key
Create a `.env` file:
```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. 🚀 Run Chatbot
```bash
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY` - Your Groq API key (required)

### Customization
Edit `app.py` to:
- Change the model (default: `gemma2-9b-it`)
- Modify the system prompt
- Adjust temperature settings

## 📁 Files

- `app.py` - Main chatbot application
- `requirements.txt` - Python dependencies
- `README.md` - This file
- `.env` - Your API keys (create this)

## 🔗 Get API Key

Get a free Groq API key from: https://console.groq.com/

## 💡 Usage

1. Start the app: `streamlit run app.py`
2. Open your browser to the displayed URL
3. Type your questions and get AI-powered responses!

---

**Simple, Clean, Effective! 🚀**

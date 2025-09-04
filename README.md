# Chat+ with Voice

A powerful document-aware chat application with multi-model support, voice interaction (STT/TTS), cost tracking, and real-time streaming responses.

## Features

- 📄 **Multi-Document Support**: Upload and manage multiple PDF, Word, and text documents
- 🤖 **Multi-Model Selection**: Switch between Small, Medium, and Large language models  
- 🎤 **Voice Input**: Record questions using built-in Speech-to-Text (Whisper)
- 🔊 **Voice Responses**: Natural Text-to-Speech with sentence highlighting (Kokoro)
- 💰 **Cost & Token Tracking**: Real-time tracking of API usage and costs
- 🔄 **Streaming Responses**: Real-time streaming with proper markdown rendering
- 📝 **Multi-line Input**: Support for multi-line messages (Shift+Enter for new line)
- 🗑️ **Document Management**: Individual document removal and session clearing
- 🎨 **Clean UI**: Modern, responsive interface with voice mode toggle

## Requirements

- **Python 3.12** (specifically required - not 3.11 or 3.13)
- macOS with Apple Silicon (M1/M2/M3) for optimal MLX performance
- OpenAI API key for LLM functionality

## Setup

### Quick Setup (Recommended)

1. **Clone and setup**:
```bash
git clone https://github.com/alexwday/call_summary.git
cd call_summary
./setup.sh  # Automated setup script for Python 3.12
```

### Manual Setup

1. **Install Python 3.12**:
```bash
# macOS (Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt install python3.12 python3.12-venv

# Verify installation
python3.12 --version  # Should show Python 3.12.x
```

2. **Create virtual environment with Python 3.12**:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python version in venv
python --version  # Must show Python 3.12.x
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings (API keys, etc.)
```

The `.env` file from Aegis project works directly - just copy it over.

5. **Run the application**:
```bash
python app.py
```

6. **Open in browser**:
- Regular Chat: `http://localhost:5003`
- Voice Mode: `http://localhost:5003?voice=true`

## Usage

### Basic Chat
1. Type your message in the input field
2. Press Enter to send (or Shift+Enter for new line)
3. Watch the response stream in real-time

### Voice Mode
1. Enable "Voice Responses" toggle in the header
2. Hold the microphone button to record your question
3. Release to transcribe and send
4. Listen to AI responses with synchronized sentence highlighting

### Document Upload
1. Click "📎 Upload Documents" to select files
2. Supported formats: PDF, DOCX, DOC, TXT
3. Multiple files can be uploaded at once
4. Documents remain in context for all subsequent messages

### Model Selection
1. Use the dropdown in the header to select model size:
   - **Small**: Fast, cost-effective for simple tasks
   - **Medium**: Balanced performance and cost
   - **Large**: Best quality for complex analysis
2. Model name is displayed next to the selector
3. Selection persists for the session

### Document Management
- Click the × next to any document to remove it from context
- Click "Clear All" to reset the session completely
- Removed documents are deleted from the server

### Cost Tracking
- Token count shows total input + output tokens used
- Cost display shows cumulative cost for the session
- Updates after each message exchange

## Configuration

### Environment Variables

```bash
# Authentication
AUTH_METHOD=api_key  # or oauth
API_KEY=your-openai-api-key

# LLM Models
LLM_MODEL_SMALL=gpt-4o-mini
LLM_MODEL_MEDIUM=gpt-4o
LLM_MODEL_LARGE=gpt-4o

# Cost Configuration (per 1000 tokens)
LLM_COST_INPUT_SMALL=0.00015
LLM_COST_OUTPUT_SMALL=0.0006
LLM_COST_INPUT_MEDIUM=0.0025
LLM_COST_OUTPUT_MEDIUM=0.01
LLM_COST_INPUT_LARGE=0.005
LLM_COST_OUTPUT_LARGE=0.015

# Temperature Settings
LLM_TEMPERATURE_SMALL=0.3
LLM_TEMPERATURE_MEDIUM=0.5
LLM_TEMPERATURE_LARGE=0.7

# Max Tokens
LLM_MAX_TOKENS_SMALL=1000
LLM_MAX_TOKENS_MEDIUM=2000
LLM_MAX_TOKENS_LARGE=4000

# Logging
LOG_LEVEL=INFO

# SSL (optional)
SSL_VERIFY=false
SSL_CERT_PATH=path/to/cert.pem

# OAuth (optional, if AUTH_METHOD=oauth)
OAUTH_ENDPOINT=https://your-oauth-endpoint
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
```

## Project Structure

```
call_summary/
├── app.py                  # Flask web application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── templates/
│   └── chat.html          # Web interface with Chat+ UI
├── src/call_summary/
│   ├── main.py            # Core chat logic with model selection
│   ├── connections/
│   │   ├── llm_connector.py    # LLM API with cost tracking
│   │   └── oauth_connector.py  # OAuth authentication
│   └── utils/
│       ├── settings.py    # Configuration management
│       ├── logging.py     # Logging utilities
│       └── ssl.py         # SSL configuration
└── uploads/               # Temporary file storage
```

## Supported File Types

- **PDF** (.pdf): Extracts text from all pages
- **Word** (.docx): Extracts paragraphs and tables
- **Text** (.txt): Plain text files
- **XML** (.xml): Including FactSet transcripts

## Development

The project uses utilities and connections from the Aegis project:
- Authentication (OAuth/API key)
- LLM connections (OpenAI)
- Logging and configuration
- SSL support

## Troubleshooting

### Python Version Issues
If you encounter Python version conflicts:
```bash
# Check current Python version
python --version

# If not 3.12, remove existing venv
rm -rf venv

# Recreate with Python 3.12
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### MLX Installation Issues
If MLX modules fail to install on non-Apple Silicon:
- MLX is optimized for Apple Silicon (M1/M2/M3)
- On Intel Macs or Linux, voice features may have reduced performance

### Quick Python 3.12 Check
Run this to verify your setup:
```bash
./setup.sh  # This will check and configure Python 3.12 automatically
```

## License

MIT
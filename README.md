# Chat+

A powerful document-aware chat application with multi-model support, cost tracking, and real-time streaming responses.

## Features

- 📄 **Multi-Document Support**: Upload and manage multiple PDF, Word, and text documents
- 🤖 **Multi-Model Selection**: Switch between Small, Medium, and Large language models  
- 💰 **Cost & Token Tracking**: Real-time tracking of API usage and costs
- 🔄 **Streaming Responses**: Real-time streaming with proper markdown rendering
- 📝 **Multi-line Input**: Support for multi-line messages (Shift+Enter for new line)
- 🗑️ **Document Management**: Individual document removal and session clearing
- 🎨 **Clean UI**: Modern, responsive interface with reduced font size for better readability

## Setup

1. **Clone the repository**:
```bash
git clone https://github.com/alexwday/call_summary.git
cd call_summary
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
Navigate to `http://localhost:5001`

## Usage

### Basic Chat
1. Type your message in the input field
2. Press Enter to send (or Shift+Enter for new line)
3. Watch the response stream in real-time

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

## License

MIT
# Document Chat Assistant

A conversational AI chatbot with document upload capabilities. Upload PDFs, Word documents, or text files and have intelligent conversations about their content.

## Features

- 📚 **Document Upload**: Support for PDF, Word (.docx), and text files
- 💬 **Conversational Interface**: Natural chat interface with markdown support
- 🔄 **Streaming Responses**: Real-time streaming of AI responses
- 📝 **Long Document Support**: Handle documents with 30+ pages
- 🎨 **Clean UI**: Modern, responsive web interface
- 🔐 **Secure**: Uses OAuth or API key authentication

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
Navigate to `http://localhost:5000`

## Usage

1. **Upload Documents**: Click the "Upload Documents" button to upload PDF or Word files
2. **Chat**: Type your questions in the chat input and press Enter
3. **Clear Session**: Use the "Clear All" button to remove documents and start fresh

## Environment Variables

The application uses the same environment variables as the Aegis project:

```bash
# Authentication
AUTH_METHOD=api_key  # or oauth
API_KEY=your-openai-api-key

# LLM Models
LLM_MODEL_SMALL=gpt-4o-mini
LLM_MODEL_MEDIUM=gpt-4o
LLM_MODEL_LARGE=gpt-4o

# Logging
LOG_LEVEL=INFO

# SSL (optional)
SSL_VERIFY=false
SSL_CERT_PATH=path/to/cert.pem
```

## Project Structure

```
call_summary/
├── app.py                  # Flask web application
├── src/call_summary/       # Main application code
│   ├── main.py            # Core chat logic
│   ├── document_processor.py  # Document handling
│   ├── connections/       # API connectors (from Aegis)
│   └── utils/            # Utilities (from Aegis)
├── templates/            # HTML templates
│   └── chat.html        # Chat interface
├── uploads/             # Temporary file storage
└── requirements.txt     # Python dependencies
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
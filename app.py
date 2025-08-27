"""
Flask web application for document chatbot.
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, Response, session
from werkzeug.utils import secure_filename
import docx
import PyPDF2
from pathlib import Path
from src.call_summary.main import model
from src.call_summary.utils.logging import get_logger

logger = get_logger()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store documents in session (in production, use a database)
SESSIONS = {}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path):
    """Extract text from PDF file."""
    text = []
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text.append(page.extract_text())
        return '\n'.join(text)
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return f"Error reading PDF: {str(e)}"


def extract_text_from_docx(file_path):
    """Extract text from Word document."""
    try:
        doc = docx.Document(file_path)
        paragraphs = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)
        
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    paragraphs.append(' | '.join(row_text))
        
        return '\n'.join(paragraphs)
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        return f"Error reading Word document: {str(e)}"


def extract_text_from_file(file_path, filename):
    """Extract text based on file type."""
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension in ['docx', 'doc']:
        return extract_text_from_docx(file_path)
    elif extension == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "Unsupported file type"


@app.route('/')
def index():
    """Main chat interface."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        SESSIONS[session['session_id']] = {
            'documents': [],
            'messages': []
        }
    return render_template('chat.html')


@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload."""
    try:
        if 'session_id' not in session:
            return jsonify({'error': 'No session found'}), 400
        
        session_id = session['session_id']
        
        if session_id not in SESSIONS:
            SESSIONS[session_id] = {
                'documents': [],
                'messages': []
            }
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PDF or Word documents.'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{session_id}_{uuid.uuid4().hex[:8]}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Extract text
        text_content = extract_text_from_file(file_path, filename)
        
        # Store document content
        SESSIONS[session_id]['documents'].append({
            'filename': filename,
            'content': text_content,
            'path': file_path
        })
        
        # Clean up file after extraction (optional)
        # os.remove(file_path)
        
        logger.info(f"Document uploaded: {filename} for session {session_id}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'Successfully uploaded {filename}',
            'document_count': len(SESSIONS[session_id]['documents'])
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        if 'session_id' not in session:
            return jsonify({'error': 'No session found'}), 400
        
        session_id = session['session_id']
        
        if session_id not in SESSIONS:
            SESSIONS[session_id] = {
                'documents': [],
                'messages': []
            }
        
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Add user message to history
        SESSIONS[session_id]['messages'].append({
            'role': 'user',
            'content': message
        })
        
        # Prepare conversation with documents
        conversation = {
            'messages': SESSIONS[session_id]['messages']
        }
        
        # Add documents if available
        if SESSIONS[session_id]['documents']:
            conversation['documents'] = [doc['content'] for doc in SESSIONS[session_id]['documents']]
        
        # Stream response
        def generate():
            assistant_message = ""
            for chunk in model(conversation):
                if chunk.get('type') == 'assistant':
                    content = chunk.get('content', '')
                    assistant_message += content
                    # Escape the content properly for SSE
                    # SSE lines cannot contain newlines, they must be escaped or sent as separate events
                    escaped_content = content.replace('\n', '\\n').replace('\r', '\\r')
                    yield f"data: {escaped_content}\n\n"
                elif chunk.get('type') == 'error':
                    yield f"data: ERROR: {chunk.get('content', 'Unknown error')}\n\n"
            
            # Store assistant message
            if assistant_message:
                SESSIONS[session_id]['messages'].append({
                    'role': 'assistant',
                    'content': assistant_message
                })
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/clear', methods=['POST'])
def clear_session():
    """Clear session documents and messages."""
    try:
        if 'session_id' in session:
            session_id = session['session_id']
            
            # Clean up uploaded files
            if session_id in SESSIONS:
                for doc in SESSIONS[session_id].get('documents', []):
                    if 'path' in doc and os.path.exists(doc['path']):
                        os.remove(doc['path'])
                
                # Clear session data
                SESSIONS[session_id] = {
                    'documents': [],
                    'messages': []
                }
            
            logger.info(f"Session cleared: {session_id}")
        
        return jsonify({'success': True, 'message': 'Session cleared'})
        
    except Exception as e:
        logger.error(f"Clear session error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """Get current session status."""
    try:
        if 'session_id' not in session:
            return jsonify({
                'session_id': None,
                'document_count': 0,
                'message_count': 0
            })
        
        session_id = session['session_id']
        
        if session_id not in SESSIONS:
            SESSIONS[session_id] = {
                'documents': [],
                'messages': []
            }
        
        return jsonify({
            'session_id': session_id,
            'document_count': len(SESSIONS[session_id]['documents']),
            'message_count': len(SESSIONS[session_id]['messages']),
            'documents': [doc['filename'] for doc in SESSIONS[session_id]['documents']]
        })
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
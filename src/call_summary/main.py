"""
Simple Document Chatbot - Main Module.

A conversational AI chatbot with document upload capabilities.
Supports Word (.docx) and PDF files for context-aware conversations.
"""

import uuid
from typing import Dict, List, Any, Generator, Optional
from src.call_summary.utils.logging import get_logger
from src.call_summary.utils.settings import config
from src.call_summary.utils.ssl import setup_ssl
from src.call_summary.connections.oauth_connector import setup_authentication
from src.call_summary.connections.llm_connector import stream as llm_stream
# Prompts removed - using inline basic prompt

logger = get_logger()


def chat_with_documents(
    messages: List[Dict[str, str]], 
    documents: Optional[List[str]] = None,
    model_size: str = 'large',
    prompt_mode: str = 'text'
) -> Generator[Dict[str, str], None, None]:
    """
    Stream chat responses with optional document context.
    
    Args:
        messages: Conversation history from the user
        documents: Optional list of document contents to include in context
        prompt_mode: Either 'text' for markdown formatting or 'voice' for spoken style
        
    Yields:
        Response chunks with streaming text
    """
    execution_id = str(uuid.uuid4())
    logger.info(f"Starting chat session {execution_id} with prompt_mode: {prompt_mode}")
    
    try:
        # Setup SSL first
        ssl_config = setup_ssl()
        
        # Setup authentication with execution_id and ssl_config
        auth_config = setup_authentication(execution_id, ssl_config)
        
        context = {
            "execution_id": execution_id,
            "auth_config": auth_config,
            "ssl_config": ssl_config
        }
        
        # Build conversation with system prompt
        enhanced_messages = []
        
        # Choose prompt based on mode
        if prompt_mode == 'voice':
            # Voice mode prompt - optimized for Kokoro TTS
            system_prompt = """You are having a natural voice conversation with the user. Your responses will be converted to speech using Kokoro TTS and played back as audio.

IMPORTANT GUIDELINES FOR KOKORO TTS VOICE RESPONSES:

PUNCTUATION & PACING:
- Use proper punctuation to guide natural speech rhythm and intonation.
- Add commas for natural breathing pauses and speech flow.
- Use periods to mark clear sentence endings with appropriate pauses.
- Include question marks to trigger rising intonation for questions.
- Add exclamation points for emphasis when expressing enthusiasm or importance!
- Use ellipses... to indicate thoughtful pauses or trailing thoughts.

SENTENCE STRUCTURE:
- Keep sentences at moderate length, around 15-25 words for optimal flow.
- Break complex ideas into multiple shorter sentences.
- Vary sentence length to create natural conversational rhythm.
- Start with complete thoughts and provide context, as Kokoro performs better with full sentences.

FORMATTING & CONTENT:
- For regular text: Avoid markdown formatting like asterisks or underscores.
- EXCEPTION: When presenting tabular data, use proper markdown table formatting with | separators.
- For tables: Keep the structure clear with headers, separator rows, and data rows.
- Spell out numbers under twenty in prose (e.g., "fifteen" not "15").
- In tables: Numbers can remain as digits for clarity.
- Expand abbreviations in prose (e.g., "for example" not "e.g.").
- Use "dollars" instead of "$", "degrees" instead of "°" in prose.

CONVERSATIONAL TONE:
- Speak as if you're having a friendly, in-person conversation.
- Use contractions naturally (e.g., "I'll", "you're", "it's") for more fluid speech.
- Add transitional phrases like "Well," "Now," "So," to sound more natural.
- Include acknowledgments like "I see," "That's interesting," when appropriate.

DOCUMENT REFERENCES:
- When discussing documents, describe them conversationally.
- Say things like: "Looking at the document you shared, I can see that..."
- Avoid technical references, instead use: "The file mentions that..." or "According to what you've uploaded..."

Remember: Every word will be spoken aloud. Focus on natural speech patterns, proper punctuation for pacing, and clear, conversational language that sounds engaging when heard rather than read."""
        else:
            # Text mode prompt - formatted for reading
            system_prompt = """You are a helpful AI assistant who will be analyzing documents that the user provides. 

FORMATTING GUIDELINES:
- Use markdown formatting to structure your responses clearly
- Use **bold** for emphasis and *italics* for subtle highlights
- Create bullet points and numbered lists when appropriate
- Use code blocks with ``` for technical content
- Include headings with ## when organizing longer responses
- Add line breaks for better readability
- When referencing documents, format quotes and citations clearly

TABLE FORMATTING:
- When creating markdown tables, use proper structure:
  - First row: Headers separated by |
  - Second row: Alignment indicators (|---|---|)
  - Following rows: Data rows, each on a new line
- IMPORTANT: Each table row must be on its own line
- Example:
  | Header 1 | Header 2 | Header 3 |
  |----------|----------|----------|
  | Data 1   | Data 2   | Data 3   |
  | Data 4   | Data 5   | Data 6   |

When documents are uploaded, you can reference them to answer questions, provide insights, and help the user understand their content with well-formatted, easy-to-read responses."""
        
        enhanced_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add document content if provided
        if documents:
            document_context = "\n\n===== UPLOADED DOCUMENTS =====\n\n"
            for i, doc in enumerate(documents, 1):
                # Handle both old format (string) and new format (dict with metadata)
                if isinstance(doc, str):
                    # Legacy format - just content string
                    document_context += f"Document {i}:\n{doc}\n\n"
                    document_context += "=" * 50 + "\n\n"
                elif isinstance(doc, dict):
                    # New format with metadata
                    metadata = doc.get('metadata', {})
                    content = doc.get('content', '')
                    
                    # Create structured document header with metadata
                    document_context += f"===== DOCUMENT {i} =====\n"
                    document_context += f"[FILE METADATA]\n"
                    document_context += f"  • Filename: {metadata.get('original_filename', doc.get('filename', 'Unknown'))}\n"
                    document_context += f"  • File Type: {metadata.get('file_extension', 'Unknown').upper()}\n"
                    document_context += f"  • File Size: {metadata.get('file_size_human', 'Unknown')}\n"
                    document_context += f"  • Upload Time: {metadata.get('upload_timestamp', 'Unknown')}\n"
                    document_context += f"  • Last Modified: {metadata.get('last_modified', 'Unknown')}\n"
                    document_context += f"  • Document ID: {doc.get('id', 'Unknown')}\n"
                    document_context += f"\n[FILE CONTENT]\n"
                    document_context += f"{content}\n\n"
                    document_context += "=" * 50 + "\n\n"
            
            enhanced_messages.append({
                "role": "system",
                "content": f"The user has uploaded the following documents for reference:\n{document_context}"
            })
            
            logger.info(f"Added {len(documents)} documents to context")
        
        # Add the conversation messages
        enhanced_messages.extend(messages)
        
        # Stream response from LLM
        logger.info(f"Sending request to LLM with {len(enhanced_messages)} messages using model: {model_size}")
        
        for chunk in llm_stream(enhanced_messages, context, model_size=model_size):
            # Handle different chunk types
            if chunk.get("type") == "usage_stats":
                # Pass through usage statistics
                yield {
                    "type": "usage",
                    "usage": chunk.get("usage", {}),
                    "metrics": chunk.get("metrics", {})
                }
            elif chunk.get("choices") and len(chunk["choices"]) > 0:
                # Extract text content from chunk
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield {
                        "type": "assistant",
                        "content": content
                    }
            elif chunk.get("usage"):
                # Handle usage in regular chunks (fallback)
                yield {
                    "type": "usage",
                    "usage": chunk["usage"]
                }
            
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        yield {
            "type": "error",
            "content": f"An error occurred: {str(e)}"
        }


def model(conversation: Dict[str, Any]) -> Generator[Dict[str, str], None, None]:
    """
    Main entry point that mimics Aegis model interface.
    
    Args:
        conversation: Dictionary with 'messages' and optional 'documents'
        
    Yields:
        Response chunks
    """
    messages = conversation.get("messages", [])
    documents = conversation.get("documents", None)
    model_size = conversation.get("model", "large")
    prompt_mode = conversation.get("prompt_mode", "basic")
    
    for chunk in chat_with_documents(messages, documents, model_size, prompt_mode):
        yield chunk
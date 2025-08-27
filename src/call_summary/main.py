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

logger = get_logger()


def chat_with_documents(
    messages: List[Dict[str, str]], 
    documents: Optional[List[str]] = None
) -> Generator[Dict[str, str], None, None]:
    """
    Stream chat responses with optional document context.
    
    Args:
        messages: Conversation history from the user
        documents: Optional list of document contents to include in context
        
    Yields:
        Response chunks with streaming text
    """
    execution_id = str(uuid.uuid4())
    logger.info(f"Starting chat session {execution_id}")
    
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
        
        # Simple, conversational system prompt
        system_prompt = """You are a helpful and friendly AI assistant. You can have natural conversations 
        and help analyze documents when they are provided. You respond in a clear, conversational tone
        and ALWAYS use proper markdown formatting for structure and clarity.
        
        When creating lists, use proper markdown syntax:
        - Use "- " or "* " for bullet points
        - Use "1. " for numbered lists
        - Use "**bold**" for emphasis
        - Use headers (# ## ###) for sections
        - Use `code` for inline code
        - Use tables when appropriate"""
        
        enhanced_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add document content if provided
        if documents:
            document_context = "\n\n===== UPLOADED DOCUMENTS =====\n\n"
            for i, doc_content in enumerate(documents, 1):
                document_context += f"Document {i}:\n{doc_content}\n\n"
                document_context += "=" * 50 + "\n\n"
            
            enhanced_messages.append({
                "role": "system",
                "content": f"The user has uploaded the following documents for reference:\n{document_context}"
            })
            
            logger.info(f"Added {len(documents)} documents to context")
        
        # Add the conversation messages
        enhanced_messages.extend(messages)
        
        # Stream response from LLM
        logger.info(f"Sending request to LLM with {len(enhanced_messages)} messages")
        
        for chunk in llm_stream(enhanced_messages, context):
            # Extract text content from chunk
            if chunk.get("choices") and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield {
                        "type": "assistant",
                        "content": content
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
    
    for chunk in chat_with_documents(messages, documents):
        yield chunk
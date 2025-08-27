"""
Connections module exports.
"""

# OAuth exports
from .oauth_connector import setup_authentication, get_oauth_token

# LLM exports
from .llm_connector import (
    complete,
    stream,
    complete_with_tools,
    embed,
    embed_batch,
    check_connection,
)

__all__ = [
    # OAuth
    "setup_authentication",
    "get_oauth_token",
    # LLM
    "complete",
    "stream",
    "complete_with_tools",
    "embed",
    "embed_batch",
    "check_connection",
]
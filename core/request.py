from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime


@dataclass
class Request:
    """Standardized request contract for runtime services.

    Attributes:
        id: Unique identifier for the request.
        service: Target service name.
        prompt: User prompt or query.
        session_id: Identifier for the session.
        conversation_id: Identifier for the conversation.
        metadata: Arbitrary metadata dictionary.
        attachments: List of attached files or references.
        options: Configuration options for processing.
        created_at: Timestamp when request was created.
    """
    id: str
    service: str
    prompt: str
    session_id: str
    conversation_id: str
    metadata: Dict[str, Any]
    attachments: list
    options: dict
    created_at: datetime


@dataclass
class Response:
    """Standardized response contract for runtime services.

    Attributes:
        success: Boolean indicating success/failure.
        content: Response content or result.
        error: Error message if failed.
        metadata: Arbitrary metadata dictionary.
        tokens_used: Token usage statistics.
        execution_time: Execution duration.
        created_at: Timestamp when response was created.
    """
    success: bool
    content: Any
    error: Optional[str]
    metadata: Dict[str, Any]
    tokens_used: int
    execution_time: float
    created_at: datetime
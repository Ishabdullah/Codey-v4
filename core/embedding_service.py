from datetime import datetime
from typing import Any, Dict, Optional
from core.base_service import BaseService
from core.request import Request, Response
from core.service_descriptor import ServiceDescriptor


class EmbeddingService(BaseService):
    """Service for text embedding operations."""

    def __init__(self, embedding_model, embedding_store=None):
        self.embedding_model = embedding_model
        self.embedding_store = embedding_store

    @property
    def name(self) -> str:
        return "embedding"

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def descriptor(self) -> ServiceDescriptor:
        return ServiceDescriptor(
            name="embedding",
            display_name="Embedding",
            description="Text embedding generation and semantic search",
            version="1.0.0",
            capabilities=["embed", "embed_batch", "search", "store", "chunk_text"],
            supported_intents=["embed", "semantic_search"],
            dependencies=[]
        )

    def handle_request(self, request: Request) -> Response:
        """Process embedding request based on action in options."""
        action = request.options.get("action")
        params = request.options.get("params", {})

        try:
            if action == "embed":
                text = params.get("text", "")
                result = self.embedding_model.embed(text)
                result = result.hex() if result else None

            elif action == "embed_batch":
                texts = params.get("texts", [])
                result = self.embedding_model.embed_batch(texts)
                result = [r.hex() if r else None for r in result] if result else None

            elif action == "store":
                filepath = params.get("filepath", "")
                content = params.get("content", "")
                from core.embeddings import chunk_text
                chunks = chunk_text(content)
                stored = 0
                if self.embedding_store:
                    for chunk, start, end in chunks:
                        emb = self.embedding_model.embed(chunk)
                        if emb:
                            self.embedding_store.store(filepath, start, end, emb)
                            stored += 1
                result = stored

            elif action == "search":
                query = params.get("query", "")
                limit = params.get("limit", 5)
                query_emb = self.embedding_model.embed(query)
                if query_emb and self.embedding_store:
                    result = self.embedding_store.search(query_emb, limit)
                else:
                    result = []

            elif action == "chunk_text":
                text = params.get("text", "")
                size = params.get("size", 500)
                overlap = params.get("overlap", 50)
                from core.embeddings import chunk_text
                result = chunk_text(text, size, overlap)

            else:
                return Response(
                    success=False,
                    content=None,
                    error=f"Unknown embedding action: {action}",
                    metadata={},
                    tokens_used=0,
                    execution_time=0.0,
                    created_at=datetime.now()
                )

            return Response(
                success=True,
                content=result,
                error=None,
                metadata={},
                tokens_used=0,
                execution_time=0.0,
                created_at=datetime.now()
            )

        except Exception as e:
            return Response(
                success=False,
                content=None,
                error=str(e),
                metadata={},
                tokens_used=0,
                execution_time=0.0,
                created_at=datetime.now()
            )
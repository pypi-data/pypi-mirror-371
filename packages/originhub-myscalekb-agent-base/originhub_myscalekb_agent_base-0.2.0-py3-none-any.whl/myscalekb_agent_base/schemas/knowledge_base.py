from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class KnowledgeBaseType(str, Enum):
    GENERAL = "general"
    PAPER = "paper"
    PATENT = "patent"
    BOOK = "book"


class KnowledgeScope(BaseModel):
    """Represents a specific collection or a selection of documents within a knowledge base."""

    kb_type: Optional[KnowledgeBaseType] = Field(
        default=None,
        description="The type of the collection this knowledge belongs to.",
        examples=[KnowledgeBaseType.PAPER],
    )
    kb_id: Optional[str] = Field(
        default=None, 
        description="Unique identifier for the knowledge base.", 
        examples=["s2"]
    )
    doc_ids: List[int] = Field(
        description="List of document IDs. An empty list indicates that all documents within the knowledge base are included.",
        default=[],
        examples=[[2988078]],
    )

    @model_validator(mode='after')
    def validate_scope(self):
        """Validate that either (kb_type and kb_id) or doc_ids is provided."""
        has_kb_info = self.kb_type is not None and self.kb_id is not None
        has_doc_ids = self.doc_ids and len(self.doc_ids) > 0
        
        if not has_kb_info and not has_doc_ids:
            raise ValueError(
                "Either both 'kb_type' and 'kb_id' must be provided, or 'doc_ids' must be non-empty"
            )
        
        return self


class KnowledgeChunkScope(BaseModel):
    """Represents a specific collection or a selection of documents within a knowledge base."""

    kb_type: KnowledgeBaseType = Field(
        description="The type of the collection this knowledge belongs to.",
        examples=[KnowledgeBaseType.PAPER],
    )
    kb_id: str = Field(description="Unique identifier for the knowledge base.", examples=["s2"])
    doc_id: int = Field(description="Globally unique identifier.", examples=[2988078])
    chunk_ids: List[int] = Field(description="List of chunk IDs.", default=[])

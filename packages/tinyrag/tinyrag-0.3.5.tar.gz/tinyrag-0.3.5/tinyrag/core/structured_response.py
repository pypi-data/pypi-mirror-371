"""
Structured response formatting with citations and source tracking
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import json


@dataclass
class Source:
    """Represents a source document with metadata"""
    id: str
    text: str
    score: float
    source_file: Optional[str] = None
    chunk_index: Optional[int] = None
    document_type: Optional[str] = None
    page_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text[:200] + "..." if len(self.text) > 200 else self.text,
            "score": round(self.score, 3),
            "source_file": self.source_file,
            "chunk_index": self.chunk_index,
            "document_type": self.document_type,
            "page_number": self.page_number
        }


@dataclass
class StructuredResponse:
    """Structured response with answer and sources"""
    query: str
    answer: str
    sources: List[Source]
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "sources": [source.to_dict() for source in self.sources],
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "source_count": len(self.sources)
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to formatted JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_markdown(self) -> str:
        """Convert to formatted Markdown with citations"""
        md_parts = [
            f"# Query: {self.query}\n",
            f"## Answer\n{self.answer}\n",
            "## Sources\n"
        ]
        
        for i, source in enumerate(self.sources, 1):
            source_info = []
            if source.source_file:
                source_info.append(f"**File:** {source.source_file}")
            if source.document_type:
                source_info.append(f"**Type:** {source.document_type}")
            if source.page_number:
                source_info.append(f"**Page:** {source.page_number}")
            if source.chunk_index is not None:
                source_info.append(f"**Chunk:** {source.chunk_index}")
            
            source_details = " | ".join(source_info) if source_info else "**Direct Text Input**"
            
            md_parts.append(f"### [{i}] {source_details}")
            md_parts.append(f"**Relevance Score:** {source.score:.3f}")
            md_parts.append(f"**Content Preview:** {source.text[:300]}{'...' if len(source.text) > 300 else ''}\n")
        
        if self.confidence:
            md_parts.append(f"**Overall Confidence:** {self.confidence:.3f}")
        
        if self.processing_time:
            md_parts.append(f"**Processing Time:** {self.processing_time:.2f}s")
        
        return "\n".join(md_parts)
    
    def to_text(self) -> str:
        """Convert to clean text format with citations"""
        parts = [
            f"Question: {self.query}",
            f"Answer: {self.answer}",
            "",
            "Sources:"
        ]
        
        for i, source in enumerate(self.sources, 1):
            source_name = source.source_file or f"Text Input {i}"
            parts.append(f"[{i}] {source_name} (Score: {source.score:.3f})")
            if source.page_number:
                parts.append(f"    Page: {source.page_number}")
            parts.append(f"    Preview: {source.text[:150]}{'...' if len(source.text) > 150 else ''}")
            parts.append("")
        
        if self.confidence:
            parts.append(f"Confidence: {self.confidence:.3f}")
        
        return "\n".join(parts)
    
    def __str__(self) -> str:
        """Default string representation"""
        return self.to_text()


class ResponseFormatter:
    """Utility class for formatting different types of responses"""
    
    @staticmethod
    def format_search_results(
        query: str, 
        results: List[tuple], 
        format_type: str = "text"
    ) -> Union[str, Dict[str, Any]]:
        """Format search results in different formats
        
        Args:
            query: Original query
            results: List of (text, score, metadata) tuples
            format_type: "text", "json", "markdown", or "structured"
        """
        sources = []
        for i, (text, score, metadata) in enumerate(results):
            metadata = metadata or {}
            source = Source(
                id=f"src_{i+1}",
                text=text,
                score=score,
                source_file=metadata.get('source_file'),
                chunk_index=metadata.get('chunk_index'),
                document_type=metadata.get('document_type'),
                page_number=metadata.get('page_number')
            )
            sources.append(source)
        
        response = StructuredResponse(
            query=query,
            answer=f"Found {len(sources)} relevant results:",
            sources=sources
        )
        
        if format_type == "json":
            return response.to_dict()
        elif format_type == "markdown":
            return response.to_markdown()
        elif format_type == "structured":
            return response
        else:  # text
            return response.to_text()
    
    @staticmethod
    def format_chat_response(
        query: str,
        answer: str,
        sources: List[tuple],
        confidence: Optional[float] = None,
        processing_time: Optional[float] = None,
        format_type: str = "text"
    ) -> Union[str, Dict[str, Any]]:
        """Format chat response with citations
        
        Args:
            query: Original query
            answer: LLM generated answer
            sources: List of (text, score, metadata) tuples used as context
            confidence: Optional confidence score
            processing_time: Optional processing time
            format_type: "text", "json", "markdown", or "structured"
        """
        source_objects = []
        for i, (text, score, metadata) in enumerate(sources):
            metadata = metadata or {}
            source = Source(
                id=f"ref_{i+1}",
                text=text,
                score=score,
                source_file=metadata.get('source_file'),
                chunk_index=metadata.get('chunk_index'),
                document_type=metadata.get('document_type'),
                page_number=metadata.get('page_number')
            )
            source_objects.append(source)
        
        # Enhance answer with citation markers
        enhanced_answer = ResponseFormatter._add_citations(answer, source_objects)
        
        response = StructuredResponse(
            query=query,
            answer=enhanced_answer,
            sources=source_objects,
            confidence=confidence,
            processing_time=processing_time
        )
        
        if format_type == "json":
            return response.to_dict()
        elif format_type == "markdown":
            return response.to_markdown()
        elif format_type == "structured":
            return response
        else:  # text
            return response.to_text()
    
    @staticmethod
    def _add_citations(answer: str, sources: List[Source]) -> str:
        """Add citation markers to the answer text"""
        # Simple approach: add citations at the end of sentences
        # More sophisticated NLP could match content to sources
        if not sources:
            return answer
        
        # Add citation references
        citation_numbers = [f"[{i+1}]" for i in range(len(sources))]
        citation_text = ", ".join(citation_numbers)
        
        # Add citations at the end if not already present
        if not any(f"[{i+1}]" in answer for i in range(len(sources))):
            answer += f" {citation_text}"
        
        return answer
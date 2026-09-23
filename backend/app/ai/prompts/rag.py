from typing import List, Tuple
from backend.app.db.models.document_chunk import DocumentChunk

RAG_SYSTEM_PROMPT = """You are the Employee Support Assistant, an AI expert on internal company policies and HR guidelines.

Your task is to answer employee questions strictly and accurately based on the provided policy document excerpts below.

Rules:
1. Grounding: Rely ONLY on the information present in the Context excerpts. Do NOT assume, extrapolate, or invent policies not stated.
2. Refusal: If the answer cannot be found in the provided excerpts, clearly state: "Based on the provided company policy documents, I could not find information regarding your inquiry. Please contact the HR department directly for assistance."
3. Tone: Maintain a professional, polite, helpful, and concise tone.
4. Citations: When citing rules or facts, reference the source document name and page number if available.
"""


def build_rag_context_str(chunks: List[Tuple[DocumentChunk, float, str]]) -> str:
    """Format retrieved document chunks into clean readable context blocks."""
    if not chunks:
        return "No relevant policy documents found."

    context_blocks = []
    for idx, (chunk, score, filename) in enumerate(chunks, start=1):
        page_str = f"Page {chunk.page_number}" if chunk.page_number is not None else "Page N/A"
        block = (
            f"--- Excerpt [{idx}] ---\n"
            f"Document: {filename} | {page_str} | Relevance: {score:.2f}\n"
            f"Content:\n{chunk.content.strip()}"
        )
        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def format_rag_user_prompt(query: str, chunks: List[Tuple[DocumentChunk, float, str]]) -> str:
    """Construct user message combining retrieved context and employee query."""
    context_str = build_rag_context_str(chunks)
    return (
        f"Context excerpts from company policy documents:\n\n"
        f"{context_str}\n\n"
        f"Employee Question: {query}\n\n"
        f"Answer:"
    )

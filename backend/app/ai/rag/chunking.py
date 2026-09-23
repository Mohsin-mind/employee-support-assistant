from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import re


@dataclass
class TextChunk:
    """Represents a discrete text chunk with its source page and sequence index."""
    content: str
    chunk_index: int
    page_number: int
    metadata: Dict[str, Any] = field(default_factory=dict)


def clean_text(text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    if not text:
        return ""
    # Replace multiple whitespace/newlines with single space
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_page_text(
    page_number: int,
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    start_index: int = 0,
) -> List[TextChunk]:
    """
    Split a single page's text into overlapping chunks, respecting paragraph and sentence boundaries.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [
            TextChunk(
                content=cleaned,
                chunk_index=start_index,
                page_number=page_number,
                metadata={"length": len(cleaned)},
            )
        ]

    chunks: List[TextChunk] = []
    idx = start_index
    start = 0

    while start < len(cleaned):
        end = start + chunk_size

        if end < len(cleaned):
            # Try to break at paragraph boundary, sentence end (. ? !), or space
            split_at = -1
            for sep in ["\n\n", "\n", ". ", "? ", "! ", " "]:
                pos = cleaned.rfind(sep, start + chunk_overlap, end)
                if pos != -1:
                    split_at = pos + len(sep)
                    break
            if split_at != -1:
                end = split_at

        chunk_content = cleaned[start:end].strip()
        if chunk_content:
            chunks.append(
                TextChunk(
                    content=chunk_content,
                    chunk_index=idx,
                    page_number=page_number,
                    metadata={"length": len(chunk_content)},
                )
            )
            idx += 1

        if end >= len(cleaned):
            break

        # Move forward, respecting overlap
        start = max(start + 1, end - chunk_overlap)

    return chunks


def split_pages_into_chunks(
    pages: List[Tuple[int, str]],
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> List[TextChunk]:
    """
    Iterate over document pages and return an indexed list of TextChunks.
    """
    all_chunks: List[TextChunk] = []
    current_index = 0

    for page_number, page_text in pages:
        page_chunks = chunk_page_text(
            page_number=page_number,
            text=page_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            start_index=current_index,
        )
        all_chunks.extend(page_chunks)
        current_index += len(page_chunks)

    return all_chunks

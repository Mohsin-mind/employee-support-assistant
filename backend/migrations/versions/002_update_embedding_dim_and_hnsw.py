"""update embedding dim to 384 and add hnsw index

Revision ID: 002_update_embedding_dim_and_hnsw
Revises: 36930d3e83d1
Create Date: 2026-09-23 10:36:00.000000

"""
from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '002_phase3_rag_hnsw'
down_revision: Union[str, None] = '36930d3e83d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update embedding column dimension from 1536 to 384 (FastEmbed BGE-small-en-v1.5)
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(384);")

    # 2. Create HNSW index on embedding column for fast approximate nearest neighbor (ANN) retrieval
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
    )


def downgrade() -> None:
    # 1. Drop HNSW index
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw;")

    # 2. Revert column dimension to 1536
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536);")

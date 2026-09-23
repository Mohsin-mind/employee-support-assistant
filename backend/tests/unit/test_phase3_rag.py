import asyncio
import io
import sys
from pathlib import Path

# Ensure repository root is on sys.path
TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.db.session import AsyncSessionLocal
from backend.app.ai.rag.retrieval import retrieve_relevant_chunks
from backend.app.ai.clients.embeddings import embedding_client


def generate_mock_policy_pdf() -> bytes:
    """
    Generate a valid 3-page PDF in memory containing sample HR policy rules.
    """
    pages = [
        "Acme Corp Remote Work Policy.\nEmployees can work remotely up to 2 days per week with manager approval.\nCore working hours are 10:00 AM to 4:00 PM EST.",
        "Acme Corp Leave Policy.\nFull-time employees receive 10 days of paid sick leave per year.\nA doctor certificate is required for sick leave exceeding 3 days.",
        "Acme Corp Equipment Stipend.\nEmployees receive a 500 dollar home office equipment reimbursement stipend upon passing probation.",
    ]
    num_pages = len(pages)
    objects = []
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    kids_str = " ".join(f"{3 + i} 0 R" for i in range(num_pages))
    objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {num_pages} >>\nendobj")

    font_obj_idx = 3 + num_pages
    stream_start_idx = font_obj_idx + 1

    for i in range(num_pages):
        stream_idx = stream_start_idx + i
        page_idx = 3 + i
        objects.append(
            f"{page_idx} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_obj_idx} 0 R >> >> "
            f"/Contents {stream_idx} 0 R >>\nendobj"
        )

    objects.append(f"{font_obj_idx} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj")

    for i, text in enumerate(pages):
        stream_idx = stream_start_idx + i
        lines = text.split("\n")
        stream_cmds = ["BT", "/F1 12 Tf", "50 720 Td"]
        for line_idx, line in enumerate(lines):
            clean_line = line.replace("(", r"\(").replace(")", r"\)")
            if line_idx > 0:
                stream_cmds.append("0 -20 Td")
            stream_cmds.append(f"({clean_line}) Tj")
        stream_cmds.append("ET")
        stream_str = "\n".join(stream_cmds) + "\n"
        objects.append(
            f"{stream_idx} 0 obj\n<< /Length {len(stream_str)} >>\nstream\n{stream_str}endstream\nendobj"
        )

    body = "\n".join(objects) + "\n"
    content = "%PDF-1.4\n" + body
    pdf_out = content + f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{len(content)}\n%%EOF"
    return pdf_out.encode("latin1")


async def run_phase3_rag_tests():
    print("=== Phase 3: Manual PDF RAG End-to-End Test Suite ===")

    # 1. Test FastEmbed Vector Generation
    print("\n1. Testing Local FastEmbed Embedding Client...")
    sample_text = "Acme Corp remote work policy allows 2 remote days per week."
    vec = embedding_client.embed_query(sample_text)
    assert len(vec) == 384, f"Expected 384-dim embedding, got {len(vec)}"
    print("✓ FastEmbed generates 384-dimensional dense vectors successfully.")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 2. Upload Multi-page PDF
        print("\n2. Testing PDF Upload via POST /api/v1/documents/upload...")
        pdf_bytes = generate_mock_policy_pdf()
        files = {
            "file": ("Acme_Policy_Handbook.pdf", io.BytesIO(pdf_bytes), "application/pdf")
        }
        res = await client.post("/api/v1/documents/upload", files=files)
        assert res.status_code == 202, f"Upload failed: {res.text}"
        doc_data = res.json()["data"]
        doc_id = doc_data["id"]
        print(f"✓ Document uploaded successfully: id='{doc_id}', status='{doc_data['status']}'")

        # 3. Poll for Background Indexing Completion
        print("\n3. Waiting for Background PDF Ingestion & pgvector Indexing...")
        indexed = False
        for _ in range(30):
            await asyncio.sleep(0.5)
            status_res = await client.get(f"/api/v1/documents/{doc_id}")
            doc_status = status_res.json()["data"]["status"]
            if doc_status == "indexed":
                indexed = True
                break
            elif doc_status == "failed":
                error_msg = status_res.json()["data"].get("error_message")
                raise RuntimeError(f"Background ingestion failed: {error_msg}")

        assert indexed, "Timed out waiting for document status to become 'indexed'"
        print(f"✓ Document status is now '{doc_status}' (INDEXED).")

        # 4. Inspect Document Chunks
        print("\n4. Testing GET /api/v1/documents/{id}/chunks...")
        chunks_res = await client.get(f"/api/v1/documents/{doc_id}/chunks")
        assert chunks_res.status_code == 200
        chunks = chunks_res.json()["data"]
        assert len(chunks) >= 3, f"Expected at least 3 chunks, got {len(chunks)}"
        print(f"✓ Ingested {len(chunks)} text chunks with page tracking:")
        for c in chunks:
            print(f"  - Chunk {c['chunk_index']} (Page {c['page_number']}): {c['content'][:50]}...")

        # 5. Direct Vector Similarity Retrieval
        print("\n5. Testing pgvector Cosine Distance Search...")
        async with AsyncSessionLocal() as session:
            retrieved = await retrieve_relevant_chunks(
                session=session,
                query="How many sick leave days are allowed?",
                top_k=2,
                document_id=doc_id,
            )
            assert len(retrieved) > 0, "No chunks retrieved"
            top_chunk, score, filename = retrieved[0]
            print(f"✓ Top match (score={score:.4f}, doc='{filename}', page={top_chunk.page_number}):")
            print(f"  '{top_chunk.content.strip()}'")
            assert top_chunk.page_number == 2, f"Expected page 2 for sick leave, got {top_chunk.page_number}"
            assert "10 days of paid sick leave" in top_chunk.content

        # 6. End-to-End RAG Query via POST /api/v1/chat/query with Groq LLM
        print("\n6. Testing POST /api/v1/chat/query with Groq LLM & Sources...")
        query_payload = {
            "query": "What is the equipment reimbursement stipend for employees?",
            "top_k": 3,
            "document_id": doc_id,
        }
        chat_res = await client.post("/api/v1/chat/query", json=query_payload)
        assert chat_res.status_code == 200, f"Chat query failed: {chat_res.text}"
        chat_data = chat_res.json()["data"]
        print(f"✓ Query: '{chat_data['query']}'")
        print(f"✓ Answer from Groq:\n  {chat_data['answer']}")
        print(f"✓ Sources Cited ({len(chat_data['sources'])} sources):")
        for s in chat_data["sources"]:
            print(f"  - Doc: {s['document_name']} | Page: {s['page_number']} | Similarity: {s['similarity']:.4f}")

        assert len(chat_data["sources"]) > 0, "Sources should not be empty"
        assert "500" in chat_data["answer"], "Expected answer to mention 500 dollar stipend"
        assert chat_data["sources"][0]["page_number"] == 3

        # 7. Unanswerable Query (Anti-Hallucination Grounding Test)
        print("\n7. Testing Anti-Hallucination Grounding (Unanswerable Question)...")
        refusal_payload = {
            "query": "What is the company policy regarding bringing dogs to the office?",
            "top_k": 2,
            "document_id": doc_id,
        }
        refusal_res = await client.post("/api/v1/chat/query", json=refusal_payload)
        assert refusal_res.status_code == 200
        refusal_answer = refusal_res.json()["data"]["answer"]
        print(f"✓ Response to out-of-scope query:\n  {refusal_answer}")

        # 8. Clean up
        print("\n8. Cleaning up test document...")
        del_res = await client.delete(f"/api/v1/documents/{doc_id}")
        assert del_res.status_code == 200
        print("✓ Test document and cascaded chunks cleaned up.")

    print("\n=======================================================")
    print(" ALL PHASE 3 RAG TESTS COMPLETED & PASSED SUCCESSFULLY!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(run_phase3_rag_tests())

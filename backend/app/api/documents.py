import os
import shutil
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.research import Document, DocumentChunk
from app.schemas.research import DocumentResponse, DocumentChunkResponse
from app.rag.document_processor import extract_text_from_file
from app.rag.chunker import chunk_document_sections
from app.rag.hybrid_search import hybrid_search
from app.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a document (PDF, DOCX, TXT), extracts text, chunks it,
    computes embeddings, and indexes for pgvector hybrid retrieval.
    """
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    doc_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")

    # Read content & check size limit
    content_bytes = await file.read()
    if len(content_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum upload size limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB"
        )

    with open(save_path, "wb") as f:
        f.write(content_bytes)

    # 1. Create Document Record
    doc_record = Document(
        id=doc_id,
        filename=file.filename or "uploaded_file",
        file_type=ext,
        file_size=len(content_bytes),
        storage_path=save_path,
        processed=False,
    )
    db.add(doc_record)
    db.commit()

    # 2. Extract sections & chunk
    try:
        sections = extract_text_from_file(save_path, file.filename or "")
        chunks = chunk_document_sections(sections, document_id=doc_id)

        llm = get_llm_provider()

        # 3. Store chunks & embeddings
        for c in chunks:
            embedding = llm.get_embedding(c["content"])
            chunk_rec = DocumentChunk(
                document_id=doc_id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                metadata_json=c["metadata"],
                embedding=embedding,
            )
            db.add(chunk_rec)

        doc_record.processed = True
        doc_record.summary = f"Processed {len(sections)} sections into {len(chunks)} searchable chunks."
        db.commit()
        db.refresh(doc_record)

        return DocumentResponse(
            id=doc_record.id,
            filename=doc_record.filename,
            file_type=doc_record.file_type,
            file_size=doc_record.file_size,
            processed=doc_record.processed,
            summary=doc_record.summary,
            chunks_count=len(chunks),
            created_at=doc_record.created_at,
        )

    except Exception as e:
        logger.error("Error processing uploaded document %s: %s", file.filename, str(e))
        doc_record.processed = False
        doc_record.summary = f"Processing error: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        count = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
        results.append(
            DocumentResponse(
                id=d.id,
                filename=d.filename,
                file_type=d.file_type,
                file_size=d.file_size,
                processed=d.processed,
                summary=d.summary,
                chunks_count=count,
                created_at=d.created_at,
            )
        )
    return results


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"message": "Document and associated chunks deleted successfully"}


@router.post("/search")
def search_documents(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """
    Executes hybrid retrieval across all indexed document chunks.
    """
    chunks = db.query(DocumentChunk).all()
    if not chunks:
        return []

    llm = get_llm_provider()
    query_vec = llm.get_embedding(query)

    candidates = [
        {
            "id": c.id,
            "document_id": c.document_id,
            "content": c.content,
            "metadata": c.metadata_json,
            "embedding": c.embedding,
            "credibility_score": 0.90,  # Uploaded internal documents scored high
        }
        for c in chunks
    ]

    results = hybrid_search(query, query_vec, candidates, top_k=top_k)
    return results

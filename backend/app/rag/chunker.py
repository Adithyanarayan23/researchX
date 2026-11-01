from typing import List, Dict, Any


def chunk_document_sections(
    sections: List[Dict[str, Any]],
    document_id: str,
    target_chunk_size: int = 1000,
    overlap_size: int = 150
) -> List[Dict[str, Any]]:
    """
    Splits document sections into structured chunks with preserved metadata.
    Returns: List of chunk dictionaries ready for database storage & embedding.
    """
    chunks: List[Dict[str, Any]] = []
    chunk_counter = 0

    for sec in sections:
        text = sec.get("text", "").strip()
        page_num = sec.get("page_number", 1)
        section_name = sec.get("section", "Section")

        if not text:
            continue

        # Split into logical paragraphs first
        paragraphs = text.split("\n")
        current_chunk_words: List[str] = []
        current_char_len = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            words = para.split(" ")
            for word in words:
                current_chunk_words.append(word)
                current_char_len += len(word) + 1

                if current_char_len >= target_chunk_size:
                    chunk_text = " ".join(current_chunk_words).strip()
                    chunks.append({
                        "document_id": document_id,
                        "chunk_index": chunk_counter,
                        "content": chunk_text,
                        "metadata": {
                            "document_id": document_id,
                            "page_number": page_num,
                            "section": section_name,
                            "source_type": "uploaded_document",
                        }
                    })
                    chunk_counter += 1

                    # Keep overlap words
                    overlap_words = []
                    overlap_chars = 0
                    for w in reversed(current_chunk_words):
                        overlap_words.insert(0, w)
                        overlap_chars += len(w) + 1
                        if overlap_chars >= overlap_size:
                            break
                    current_chunk_words = overlap_words
                    current_char_len = overlap_chars

        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words).strip()
            if chunk_text:
                chunks.append({
                    "document_id": document_id,
                    "chunk_index": chunk_counter,
                    "content": chunk_text,
                    "metadata": {
                        "document_id": document_id,
                        "page_number": page_num,
                        "section": section_name,
                        "source_type": "uploaded_document",
                    }
                })
                chunk_counter += 1

    return chunks

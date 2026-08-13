import re
from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.parser import DocumentChunk

class DocumentRetriever:
    """
    RAG Context Retriever utilizing Hybrid Relevance Scoring (TF-IDF Vectorization,
    Cosine Similarity, Exact Phrase Matching, Definition Keyword Detection, and Title/Page Boosts)
    to retrieve top relevant chunks from parsed documents.
    """
    def __init__(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.chunk_texts = [chunk.text for chunk in chunks]
        if self.chunk_texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunk_texts)
        else:
            self.tfidf_matrix = None

    def get_top_chunks(self, query: str, top_k: int = 8) -> List[Tuple[DocumentChunk, float]]:
        if not self.chunks or not query.strip():
            return []

        # Default top_k to total chunks if total chunks is small
        top_k = min(top_k, len(self.chunks))
        
        similarities = np.zeros(len(self.chunks))
        if self.tfidf_matrix is not None:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        query_lower = query.lower().strip()
        query_terms = [w for w in re.findall(r'\w+', query_lower) if len(w) > 2]
        is_def_query = any(query_lower.startswith(prefix) for prefix in ["what is", "what are", "define", "definition", "explain"])

        hybrid_scores = []
        for idx, chunk in enumerate(self.chunks):
            score = float(similarities[idx])
            text_lower = chunk.text.lower()
            section_lower = chunk.section_title.lower()

            # Exact phrase match boost
            if query_lower in text_lower or (len(query_lower) > 5 and query_lower.rstrip('?') in text_lower):
                score += 0.35

            # Definition keyword indicator boost for "What is X?" queries
            if is_def_query:
                def_indicators = ["is known as", "is defined as", "is the process of", "refers to", "is a process", "is an architecture", "is a technique"]
                if any(ind in text_lower for ind in def_indicators):
                    score += 0.25
                if chunk.page_num <= 2:
                    score += 0.15

            # Heading & Opening line match boost
            if query_lower in section_lower or any(t in text_lower[:100] for t in query_terms if len(t) > 3):
                score += 0.20

            # Keyword overlap ratio boost
            if query_terms:
                matches = sum(1 for term in query_terms if term in text_lower)
                overlap_ratio = matches / len(query_terms)
                score += overlap_ratio * 0.20

            hybrid_scores.append((idx, score))

        # Sort by hybrid score descending
        hybrid_scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = hybrid_scores[:top_k]

        results = []
        for idx, score in top_indices:
            results.append((self.chunks[idx], score))

        return results

    def get_full_text(self) -> str:
        """Returns concatenated text of all chunks with citation markers."""
        full_text_pieces = []
        for chunk in self.chunks:
            full_text_pieces.append(f"[{chunk.citation_label}]\n{chunk.text}")
        return "\n\n".join(full_text_pieces)

    def get_document_metadata(self) -> dict:
        """Returns structural metadata about the document (total pages, chunks, words, sections)."""
        if not self.chunks:
            return {
                "total_pages": 0,
                "total_chunks": 0,
                "total_words": 0,
                "sections": []
            }
        total_pages = max(c.page_num for c in self.chunks)
        total_chunks = len(self.chunks)
        total_words = sum(len(c.text.split()) for c in self.chunks)
        sections = sorted(list(set(c.section_title for c in self.chunks if c.section_title and c.section_title != "General Content")))
        return {
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "total_words": total_words,
            "sections": sections
        }


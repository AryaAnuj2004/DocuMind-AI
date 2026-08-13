import re
from typing import List, Dict, Any, Optional
from src.parser import DocumentChunk
from src.retriever import DocumentRetriever

class QAEngine:
    """
    Q&A Engine for 'Ask Anything' mode with strict grounding, memory handling,
    justification citation, and source snippet highlighting.
    Uses modern google.genai SDK with multi-model fallback sequence.
    """

    @staticmethod
    def format_history_for_prompt(chat_history: List[Dict[str, str]]) -> str:
        if not chat_history:
            return "No previous conversation."
        formatted = []
        for msg in chat_history[-6:]:  # Keep last 3 turns
            role = "User" if msg.get("role") == "user" else "Assistant"
            text = msg.get("content") or msg.get("answer") or ""
            formatted.append(f"{role}: {text}")
        return "\n".join(formatted)

    @classmethod
    def answer_question(
        cls,
        query: str,
        retriever: DocumentRetriever,
        chat_history: List[Dict[str, str]],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answers user question using retrieved chunks and Gemini API.
        """
        if not api_key:
            return {
                "answer": "API Key Required: Please enter your Google Gemini API Key in the sidebar settings to use Ask Anything mode.",
                "justification": "API Key Not Provided",
                "snippet": "",
                "citation_label": "N/A"
            }

        # Retrieve top 8 relevant chunks
        top_chunks_and_scores = retriever.get_top_chunks(query, top_k=8)
        if not top_chunks_and_scores and not retriever.chunks:
            return {
                "answer": "I could not find relevant information in the uploaded document to answer your question.",
                "justification": "No matching document sections found.",
                "snippet": "",
                "citation_label": "N/A"
            }
            
        top_chunks = [item[0] for item in top_chunks_and_scores] if top_chunks_and_scores else retriever.chunks[:8]
        primary_chunk = top_chunks[0] if top_chunks else None

        # Build Document Overview Metadata safely (handles hot-reloaded session objects)
        if hasattr(retriever, 'get_document_metadata'):
            meta = retriever.get_document_metadata()
        else:
            chunks = getattr(retriever, 'chunks', [])
            total_pages = max([c.page_num for c in chunks]) if chunks else 0
            total_chunks = len(chunks)
            total_words = sum([len(c.text.split()) for c in chunks]) if chunks else 0
            sections = sorted(list(set(c.section_title for c in chunks if getattr(c, 'section_title', '') and c.section_title != "General Content"))) if chunks else []
            meta = {
                "total_pages": total_pages,
                "total_chunks": total_chunks,
                "total_words": total_words,
                "sections": sections
            }

        sections_str = ", ".join(meta['sections']) if meta['sections'] else "General Document Content"
        metadata_block = (
            "[Document Overview Metadata]\n"
            f"- Total Pages: {meta['total_pages']}\n"
            f"- Total Indexed Paragraphs/Chunks: {meta['total_chunks']}\n"
            f"- Estimated Total Word Count: {meta['total_words']}\n"
            f"- Key Document Sections: {sections_str}"
        )

        # Prepare context block with explicit citation tags and metadata
        context_blocks = [metadata_block]
        for chunk in top_chunks:
            context_blocks.append(f"[{chunk.citation_label}]\n{chunk.text}")
        context_text = "\n\n".join(context_blocks)
        
        history_text = cls.format_history_for_prompt(chat_history)

        prompt = (
            "You are a Document Assistant specializing in research comprehension and strict factual precision.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Answer the User Question strictly based on the provided Document Context and Document Overview Metadata below.\n"
            "2. For general or structural questions about the document (such as 'how many pages does it have?', 'how many paragraphs/sections are there?', 'what is the word count/length?'), use the [Document Overview Metadata] to provide a precise and direct answer.\n"
            "3. DO NOT make up outside information. If neither the text context nor the document metadata contains the answer, say 'The document does not state this.'\n"
            "4. Use the Conversation History to understand follow-up questions or references (e.g. 'it', 'the previous section').\n"
            "5. Structure your response into 3 distinct sections separated by markdown headings:\n"
            "   ### Answer\n"
            "   <Direct, clear, comprehensive answer grounded in the document context or metadata>\n\n"
            "   ### Justification\n"
            "   <Explanation of how the document supports this answer, citing specific locations e.g. Page X, Paragraph Y or Document Overview Metadata>\n\n"
            "   ### Supporting Snippet\n"
            "   \"<Verbatim quote of 1-3 sentences directly copied from text or metadata that proves the answer>\"\n\n"
            f"Conversation History:\n{history_text}\n\n"
            f"Document Context:\n{context_text}\n\n"
            f"User Question: {query}"
        )

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            candidate_models = [
                "gemini-3.5-flash-lite",
                "gemini-3.1-flash-lite",
                "gemini-2.5-flash-lite",
                "gemini-3.6-flash",
                "gemini-3.5-flash",
                "gemini-3-flash",
                "gemini-2.5-flash",
                "gemini-1.5-flash"
            ]
            raw_response = ""
            last_err = None

            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        raw_response = response.text.strip()
                        break
                except Exception as ex:
                    last_err = ex
                    err_s = str(ex).lower()
                    if any(term in err_s for term in ["quota", "429", "resourceexhausted", "limit", "exceeded", "invalid", "unauthorized"]):
                        raise ex
                    continue

            if not raw_response and last_err:
                raise last_err

            if not raw_response:
                raise ValueError("Empty response received from GenAI model.")

            # Parse sections
            answer = ""
            justification = f"Supported by {primary_chunk.citation_label}."
            snippet = primary_chunk.text[:200]
            
            if "### Answer" in raw_response:
                parts = re.split(r'###\s*', raw_response)
                for part in parts:
                    if part.startswith("Answer"):
                        answer = part.replace("Answer", "", 1).strip()
                    elif part.startswith("Justification"):
                        justification = part.replace("Justification", "", 1).strip()
                    elif part.startswith("Supporting Snippet"):
                        snippet = part.replace("Supporting Snippet", "", 1).strip().strip('"')
            else:
                answer = raw_response

            if not answer:
                answer = raw_response
                
            return {
                "answer": answer,
                "justification": justification,
                "snippet": snippet,
                "citation_label": primary_chunk.citation_label
            }

        except Exception as e:
            err_str = str(e).lower()
            if any(term in err_str for term in ["quota", "429", "resourceexhausted", "limit", "exceeded"]):
                error_msg = "Free API Quota Exhausted: Your Gemini API free tier limit or quota has been reached. Please check your API key, upgrade your quota, or try again later."
            elif any(term in err_str for term in ["invalid", "api_key", "unauthorized", "autherror", "400", "401", "403"]):
                error_msg = f"Invalid API Key: The provided API key is invalid or unauthorized. ({e})"
            else:
                error_msg = f"API Error: Unable to process query. ({e})"
                
            return {
                "answer": error_msg,
                "justification": "API Error Encountered",
                "snippet": "",
                "citation_label": "N/A"
            }

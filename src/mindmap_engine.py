import re
from typing import List, Optional
from src.parser import DocumentChunk

class MindMapEngine:
    """
    Generates Mermaid.js syntax for visual topic mind maps and concept flowcharts.
    Uses modern google.genai SDK with multi-model fallback sequence.
    """

    @classmethod
    def generate_mindmap_syntax(
        cls,
        chunks: List[DocumentChunk],
        api_key: Optional[str] = None
    ) -> str:
        if not chunks or not api_key:
            return ""

        sample_text = "\n\n".join([f"[{c.citation_label}]\n{c.text}" for c in chunks[:10]])

        prompt = (
            "You are a visual data architect.\n"
            "Task: Generate a clean, valid Mermaid.js flowchart (graph TD) representing the core topics and subtopics of the document.\n\n"
            "Requirements:\n"
            "1. Must start with 'graph TD'.\n"
            "2. Node names MUST use simple letters/numbers without special characters, spaces in node IDs, or parentheses.\n"
            "3. Use double quotes around node label text, e.g. A[\"Document Title\"] --> B[\"Main Section\"].\n"
            "4. Keep it clean with 6-10 total nodes showing main themes.\n"
            "5. Respond ONLY with raw Mermaid syntax (no markdown code blocks).\n\n"
            f"Document Context:\n{sample_text}"
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
            raw_text = ""
            last_err = None

            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        raw_text = response.text.strip()
                        break
                except Exception as ex:
                    last_err = ex
                    err_s = str(ex).lower()
                    if any(term in err_s for term in ["quota", "429", "resourceexhausted", "limit", "exceeded", "invalid", "unauthorized"]):
                        raise ex
                    continue

            if not raw_text and last_err:
                raise last_err

            raw_text = re.sub(r'^```mermaid\s*', '', raw_text, flags=re.MULTILINE)
            raw_text = re.sub(r'^```\s*', '', raw_text, flags=re.MULTILINE).strip()
            return raw_text

        except Exception:
            return ""

import json
import re
from typing import List, Dict, Any, Optional
from src.parser import DocumentChunk

class GlossaryEngine:
    """
    Extracts 5 key takeaways and a technical concept glossary with citation metadata.
    Uses modern google.genai SDK with multi-model fallback sequence.
    """

    @classmethod
    def extract_glossary_and_takeaways(
        cls,
        chunks: List[DocumentChunk],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        if not chunks or not api_key:
            return {
                "takeaways": [],
                "glossary": []
            }

        sample_text = "\n\n".join([f"[{c.citation_label}]\n{c.text}" for c in chunks[:12]])

        prompt = (
            "You are an expert research analyst and technical communicator.\n"
            "Task: Extract exactly 5 core takeaways and a Glossary of key technical terms/concepts from the document context below.\n\n"
            "Requirements:\n"
            "1. 'takeaways': Array of 5 concise, high-impact bullet point strings representing key findings or conclusions.\n"
            "2. 'glossary': Array of 4-6 objects containing keys 'term', 'definition', 'citation' (e.g. Page 1, Paragraph 2).\n"
            "3. Respond ONLY in strict valid JSON format:\n"
            "{\n"
            "  \"takeaways\": [\"Takeaway 1...\", \"Takeaway 2...\", \"Takeaway 3...\", \"Takeaway 4...\", \"Takeaway 5...\"],\n"
            "  \"glossary\": [\n"
            "    {\"term\": \"VAPT\", \"definition\": \"Vulnerability Assessment and Penetration Testing...\", \"citation\": \"Page 1, Paragraph 1\"}\n"
            "  ]\n"
            "}\n\n"
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

            raw_text = re.sub(r'^```json\s*', '', raw_text, flags=re.MULTILINE)
            raw_text = re.sub(r'^```\s*', '', raw_text, flags=re.MULTILINE).strip()

            parsed = json.loads(raw_text)
            return {
                "takeaways": parsed.get("takeaways", []),
                "glossary": parsed.get("glossary", [])
            }

        except Exception as e:
            return {
                "takeaways": [f"Unable to extract takeaways: {e}"],
                "glossary": []
            }
